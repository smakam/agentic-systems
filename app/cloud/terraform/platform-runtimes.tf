# Optional hosted adapters. Approve this access before enabling the Google adapter.
variable "google_runtime_project_id" {
  type = string
  default = ""
  description = "Project hosting the existing ADK runtime; leave empty to disable grants."
}
resource "google_project_iam_custom_role" "runtime_query" {
  count = var.google_runtime_project_id != "" ? 1 : 0
  project = var.google_runtime_project_id
  role_id = "marketplaceRuntimeQuery"
  title = "Marketplace hosted runtime queries"
  permissions = ["aiplatform.reasoningEngines.query"]
}
resource "google_project_iam_member" "runtime_query" {
  count = var.google_runtime_project_id != "" ? 1 : 0
  project = var.google_runtime_project_id
  role = google_project_iam_custom_role.runtime_query[0].name
  member = "serviceAccount:${google_service_account.runtime["web"].email}"
}
