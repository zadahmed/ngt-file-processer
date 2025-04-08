variable "project_id" {
    description = "GCP ProjectID"
    type = string
}

variable "region"  {
    description = "GCP Region"
    type = string
    default = "us-central1"
}

variable "api_image"{
    description = "Container Image for API"
    type = string
}