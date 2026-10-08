terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}
variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "asia-south1"
}
provider "google" {
  project = var.project_id
  region  = var.region
}
resource "google_project_service" "storage" {
  project            = var.project_id
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}
resource "google_project_service" "resource_manager" {
  project            = var.project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}
resource "google_storage_bucket" "state" {
  project                     = var.project_id
  name                        = "${var.project_id}-tfstate"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  depends_on = [google_project_service.storage]
}
output "state_bucket" { value = google_storage_bucket.state.name }
