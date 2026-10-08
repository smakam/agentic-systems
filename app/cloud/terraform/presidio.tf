# Mirror the digest-pinned images from compose.guardrails.yaml to Artifact
# Registry before supplying these URLs. Empty values omit the optional sidecars.
# Enabling sidecars makes Presidio available; request guardrails remain opt-in.
variable "presidio_analyzer_image" {
  type    = string
  default = ""
}
variable "presidio_anonymizer_image" {
  type    = string
  default = ""
}
locals {
  deploy_presidio = var.presidio_analyzer_image != "" && var.presidio_anonymizer_image != ""
  presidio_containers = local.deploy_presidio ? {
    presidio-analyzer = {
      image  = var.presidio_analyzer_image
      port   = 3000
      memory = "2Gi"
    }
    presidio-anonymizer = {
      image  = var.presidio_anonymizer_image
      port   = 3001
      memory = "512Mi"
    }
  } : {}
}
