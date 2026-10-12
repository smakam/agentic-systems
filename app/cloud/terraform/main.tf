locals {
  apis = toset([
    "run.googleapis.com", "sqladmin.googleapis.com", "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com", "cloudbuild.googleapis.com", "iam.googleapis.com",
    "compute.googleapis.com", "servicenetworking.googleapis.com"
  ])
  services  = toset(["web", "gateway", "mcp", "presidio", "initialize"])
  databases = toset(["market", "market_test", "market_eval", "litellm"])
  # Values are populated separately; Terraform never holds secret payloads.
  secrets = merge({
    web-database-url          = "web"
    web-read-database-url     = "web"
    web-support-key           = "web"
    mcp-read-database-url     = "mcp"
    mcp-api-key               = "mcp"
    gateway-database-url      = "gateway"
    gateway-master-key        = "gateway"
    gateway-provider-key      = "gateway"
    gateway-lakera-key        = "gateway"
    web-langfuse-secret       = "web"
    gateway-langfuse-secret   = "gateway"
    web-demo-password         = "initialize"
    bootstrap-database-url    = "initialize"
    mcp-registry-database-url = "mcp"
    mcp-embedding-key         = "mcp"
  }, (var.lyzr_secret_enabled || var.lyzr_enabled) ? { web-lyzr-api-key = "web" } : {})
}
resource "google_project_service" "api" {
  for_each           = local.apis
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = "marketplace"
  format        = "DOCKER"
  depends_on    = [google_project_service.api]
}
resource "google_service_account" "runtime" {
  for_each     = local.services
  project      = var.project_id
  account_id   = "marketplace-${each.key}"
  display_name = "Marketplace ${each.key} runtime"
  depends_on   = [google_project_service.api]
}
resource "google_sql_database_instance" "postgres" {
  project             = var.project_id
  name                = "marketplace-postgres"
  region              = var.region
  database_version    = "POSTGRES_16"
  deletion_protection = true
  settings {
    tier              = var.database_tier
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"
    activation_policy = var.database_active ? "ALWAYS" : "NEVER"
    disk_type         = "PD_SSD"
    disk_size         = var.database_disk_gb
    disk_autoresize   = false
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.private.id
      # Cloud Run uses Direct VPC egress and the Cloud SQL connector.
    }
    backup_configuration {
      enabled    = true
      start_time = "20:00"
    }
    user_labels = { purpose = "course-lab" }
  }
  depends_on = [google_project_service.api, google_service_networking_connection.sql]
}
resource "google_sql_database" "database" {
  for_each = local.databases
  project  = var.project_id
  name     = each.key
  instance = google_sql_database_instance.postgres.name
}
resource "google_project_iam_member" "sql_client" {
  for_each = toset(["web", "gateway", "mcp", "initialize"])
  project  = var.project_id
  role     = "roles/cloudsql.client"
  member   = "serviceAccount:${google_service_account.runtime[each.key].email}"
}
resource "google_secret_manager_secret" "config" {
  for_each  = local.secrets
  project   = var.project_id
  secret_id = "marketplace-${each.key}"
  replication {
    auto {}
  }
  depends_on = [google_project_service.api]
}
resource "google_secret_manager_secret_iam_member" "read" {
  for_each  = local.secrets
  project   = var.project_id
  secret_id = google_secret_manager_secret.config[each.key].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime[each.value].email}"
}
resource "google_secret_manager_secret_iam_member" "web_mcp" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.config["mcp-api-key"].secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime["web"].email}"
}

resource "google_compute_network" "private" {
  project                 = var.project_id
  name                    = "marketplace-private"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.api]
}
resource "google_compute_subnetwork" "run" {
  project                  = var.project_id
  name                     = "marketplace-run"
  region                   = var.region
  network                  = google_compute_network.private.id
  ip_cidr_range            = "10.40.0.0/24"
  private_ip_google_access = true
}
resource "google_compute_global_address" "sql" {
  project       = var.project_id
  name          = "marketplace-sql-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.private.id
}
resource "google_service_networking_connection" "sql" {
  network                 = google_compute_network.private.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.sql.name]
}
