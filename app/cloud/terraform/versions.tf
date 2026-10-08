terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
  # Supply a GCS backend through -backend-config; bootstrap the bucket separately.
  backend "gcs" {}
}
provider "google" {
  project = var.project_id
  region  = var.region
}
