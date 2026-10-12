variable "lyzr_secret_enabled" {
  type        = bool
  default     = false
  description = "Provision the secret and scoped access before private key entry."
}
variable "lyzr_agent_id" {
  type    = string
  default = ""
}
variable "google_runtime_resource" {
  type    = string
  default = ""
}
variable "lyzr_enabled" {
  type        = bool
  default     = false
  description = "Enable only after the dedicated Lyzr API-key secret has a value."
}
variable "web_image" {
  type    = string
  default = ""
}
variable "gateway_image" {
  type    = string
  default = ""
}
variable "app_origin" {
  type        = string
  default     = ""
  description = "Optional custom browser origin; empty derives the standard marketplace web URL from this project and region."
}
variable "langfuse_host" {
  type        = string
  default     = "https://jp.cloud.langfuse.com"
  description = "Langfuse Cloud regional host matching the configured project keys. Default preserves the existing course deployment."
  validation {
    condition     = contains(["https://cloud.langfuse.com", "https://us.cloud.langfuse.com", "https://jp.cloud.langfuse.com", "https://hipaa.cloud.langfuse.com"], var.langfuse_host)
    error_message = "Use the HTTPS Langfuse Cloud host for your project's region."
  }
}
variable "langfuse_public_key" {
  type    = string
  default = ""
}
variable "public_web" {
  type    = bool
  default = false
}
variable "public_mcp" {
  type    = bool
  default = false
}
variable "application_enabled" {
  type        = bool
  default     = true
  description = "Disable during gateway/init bootstrap until scoped model keys exist."
}
locals {
  deploy_gateway = var.gateway_image != ""
  deploy_web     = var.application_enabled && var.web_image != "" && local.deploy_gateway
}
resource "google_cloud_run_v2_service" "gateway" {
  count               = local.deploy_gateway ? 1 : 0
  project             = var.project_id
  name                = "marketplace-gateway"
  location            = var.region
  deletion_protection = true
  ingress             = "INGRESS_TRAFFIC_ALL"
  template {
    service_account                  = google_service_account.runtime["gateway"].email
    timeout                          = "180s"
    max_instance_request_concurrency = 4
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    vpc_access {
      egress = "PRIVATE_RANGES_ONLY"
      network_interfaces {
        network    = google_compute_network.private.name
        subnetwork = google_compute_subnetwork.run.name
      }
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance { instances = [google_sql_database_instance.postgres.connection_name] }
    }
    containers {
      name       = "gateway"
      image      = var.gateway_image
      depends_on = local.deploy_presidio ? ["presidio-analyzer", "presidio-anonymizer"] : []
      ports { container_port = 8080 }
      resources {
        limits   = { cpu = "1", memory = "2Gi" }
        cpu_idle = true
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
      env {
        name  = "OPENAI_MODEL"
        value = "openai/gpt-5.4-2026-03-05"
      }
      env {
        name  = "LANGFUSE_HOST"
        value = var.langfuse_host
      }
      env {
        name  = "LANGFUSE_PUBLIC_KEY"
        value = var.langfuse_public_key
      }
      env {
        name  = "ANTHROPIC_API_KEY"
        value = ""
      }
      dynamic "env" {
        for_each = local.deploy_presidio ? {
          PRESIDIO_ANALYZER_API_BASE   = "http://localhost:3000"
          PRESIDIO_ANONYMIZER_API_BASE = "http://localhost:3001"
        } : {}
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = { DATABASE_URL = "gateway-database-url", LITELLM_MASTER_KEY = "gateway-master-key", OPENAI_API_KEY = "gateway-provider-key", LANGFUSE_SECRET_KEY = "gateway-langfuse-secret", LAKERA_API_KEY = "gateway-lakera-key" }
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.config[env.value].secret_id
              version = "latest"
            }
          }
        }
      }
    }
    # These containers share the gateway's network namespace; no separate public
    # endpoints, service identities, or sensitive-data transit outside the service.
    dynamic "containers" {
      for_each = local.presidio_containers
      content {
        name  = containers.key
        image = containers.value.image
        resources {
          limits   = { cpu = "1", memory = containers.value.memory }
          cpu_idle = true
        }
        env {
          name  = "PORT"
          value = tostring(containers.value.port)
        }
        env {
          name  = "WORKERS"
          value = "1"
        }
        startup_probe {
          initial_delay_seconds = 0
          period_seconds        = 5
          timeout_seconds       = 3
          failure_threshold     = 48
          http_get {
            path = "/health"
            port = containers.value.port
          }
        }
      }
    }
  }
  lifecycle {
    precondition {
      condition     = (var.presidio_analyzer_image == "") == (var.presidio_anonymizer_image == "")
      error_message = "Supply both mirrored Presidio images, or leave both empty."
    }
  }
  depends_on = [google_secret_manager_secret_iam_member.read, google_project_iam_member.sql_client]
}
resource "google_cloud_run_v2_service" "application" {
  for_each            = local.deploy_web ? toset(["web", "mcp"]) : toset([])
  project             = var.project_id
  name                = "marketplace-${each.key}"
  location            = var.region
  deletion_protection = true
  ingress             = "INGRESS_TRAFFIC_ALL"
  template {
    service_account                  = google_service_account.runtime[each.key].email
    timeout                          = "180s"
    max_instance_request_concurrency = 2
    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
    vpc_access {
      egress = "PRIVATE_RANGES_ONLY"
      network_interfaces {
        network    = google_compute_network.private.name
        subnetwork = google_compute_subnetwork.run.name
      }
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance { instances = [google_sql_database_instance.postgres.connection_name] }
    }
    containers {
      image   = var.web_image
      command = each.key == "mcp" ? ["python", "-m", "marketplace.remote_mcp"] : null
      ports { container_port = 8080 }
      resources {
        limits   = { cpu = "1", memory = "1Gi" }
        cpu_idle = true
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
      dynamic "env" {
        for_each = merge({ LITELLM_URL = "${google_cloud_run_v2_service.gateway[0].uri}/v1", GATEWAY_IAM_AUDIENCE = google_cloud_run_v2_service.gateway[0].uri, DB_POOL_SIZE = "2", DB_MAX_OVERFLOW = "2", ALLOWED_ORIGINS = var.app_origin != "" ? var.app_origin : "https://marketplace-web-${data.google_project.current.number}.${var.region}.run.app", SECURE_COOKIES = "true", REMOTE_MCP_PORT = "8080", INITIALIZE_ON_STARTUP = "false", LANGFUSE_HOST = var.langfuse_host, LANGFUSE_PUBLIC_KEY = var.langfuse_public_key }, each.key == "mcp" ? { REMOTE_MCP_ALLOWED_HOSTS = "marketplace-mcp-${data.google_project.current.number}.${var.region}.run.app" } : { AGENT_TOOL_TRANSPORT = "mcp_http", SDK_MCP_URL = "https://marketplace-mcp-${data.google_project.current.number}.${var.region}.run.app/mcp", LYZR_AGENT_ID = var.lyzr_agent_id, GOOGLE_RUNTIME_RESOURCE = var.google_runtime_resource, MARKETPLACE_IDENTITY_NAMESPACE = var.project_id })
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = each.key == "web" ? merge({ DATABASE_URL = "web-database-url", READ_DATABASE_URL = "web-read-database-url", SDK_MCP_API_KEY = "mcp-api-key", LITELLM_API_KEY = "web-support-key", LANGFUSE_SECRET_KEY = "web-langfuse-secret" }, var.lyzr_enabled ? { LYZR_API_KEY = "web-lyzr-api-key" } : {}) : { READ_DATABASE_URL = "mcp-read-database-url", MCP_REGISTRY_DATABASE_URL = "mcp-registry-database-url", REMOTE_MCP_API_KEY = "mcp-api-key", LITELLM_API_KEY = "mcp-embedding-key" }
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.config[env.value].secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }
  depends_on = [google_secret_manager_secret_iam_member.read, google_secret_manager_secret_iam_member.web_mcp, google_project_iam_member.sql_client]
}
data "google_project" "current" { project_id = var.project_id }
resource "google_cloud_run_v2_service_iam_member" "gateway_invoker" {
  for_each = local.deploy_gateway ? toset(["web", "mcp"]) : toset([])
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.gateway[0].name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.runtime[each.key].email}"
}
resource "google_cloud_run_v2_service_iam_member" "web_public" {
  count    = local.deploy_web && var.public_web ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.application["web"].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
resource "google_cloud_run_v2_service_iam_member" "mcp_public" {
  count    = local.deploy_web && var.public_mcp ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.application["mcp"].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
output "service_urls" { value = merge({ for name, service in google_cloud_run_v2_service.application : name => service.uri }, local.deploy_gateway ? { gateway = google_cloud_run_v2_service.gateway[0].uri } : {}) }
