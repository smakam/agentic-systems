# Execute explicitly after credentials are populated and Cloud SQL is running.
# Creating the job does not execute it or initialize replicas on startup.
resource "google_cloud_run_v2_job" "initialize" {
  count               = var.web_image != "" ? 1 : 0
  project             = var.project_id
  name                = "marketplace-initialize"
  location            = var.region
  deletion_protection = true
  template {
    task_count  = 1
    parallelism = 1
    template {
      service_account = google_service_account.runtime["initialize"].email
      timeout         = "600s"
      max_retries     = 0
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
        command = ["python", "/app/initialize.py"]
        resources { limits = { cpu = "1", memory = "1Gi" } }
        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
        dynamic "env" {
          for_each = { BOOTSTRAP_DATABASE_URL = "bootstrap-database-url", DEMO_PASSWORD = "web-demo-password" }
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
  }
  depends_on = [google_sql_database.database, google_secret_manager_secret_iam_member.read, google_project_iam_member.sql_client]
}

output "initialization_job" {
  value = var.web_image != "" ? google_cloud_run_v2_job.initialize[0].name : null
}
