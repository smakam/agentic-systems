output "database_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}
output "database_instance" {
  value = google_sql_database_instance.postgres.name
}
output "image_repository" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}
output "runtime_identities" {
  value = { for name, identity in google_service_account.runtime : name => identity.email }
}
