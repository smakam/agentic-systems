variable "project_id" {
  type        = string
  description = "Existing billed GCP project dedicated to the shared marketplace."
}
variable "region" {
  type    = string
  default = "asia-south1"
}
variable "database_tier" {
  type        = string
  default     = "db-g1-small"
  description = "Shared-core lab tier; verify capacity before increasing. Not HA."
}
variable "database_active" {
  type        = bool
  default     = false
  description = "Start explicitly for labs; stopped by default to avoid idle compute charges."
}
variable "database_disk_gb" {
  type    = number
  default = 10
}
