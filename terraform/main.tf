provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "file_upload_bucket" {
  name                        = "file-upload-bucket-${var.project_id}"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "function_code" {
  name     = "function-code-bucket-${var.project_id}"
  location = var.region
}

data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../function"
  output_path = "${path.module}/function.zip"
}

resource "google_storage_bucket_object" "function_object" {
  name   = "function-${data.archive_file.function_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_code.name
  source = data.archive_file.function_zip.output_path
}


resource "google_project_service" "eventarc" {
  project                    = var.project_id
  service                    = "eventarc.googleapis.com"
  disable_dependent_services = false
}

data "google_storage_project_service_account" "gcs_account" {
  project = var.project_id
}

resource "google_storage_bucket_iam_member" "eventarc_storage_permission" {
  bucket = google_storage_bucket.file_upload_bucket.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

resource "google_cloudfunctions2_function" "process_file_function" {
  name        = "file-processor-function"
  description = "Function to process files uploaded to GCS"
  location    = var.region

  build_config {
    runtime     = "python310"
    entry_point = "process_file"
    source {
      storage_source {
        bucket = google_storage_bucket.function_code.name
        object = google_storage_bucket_object.function_object.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256M"
    timeout_seconds    = 60
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value     = google_storage_bucket.file_upload_bucket.name
    }
  }
}


resource "google_project_service" "services" {
  for_each = toset([
    "containerregistry.googleapis.com",
    "run.googleapis.com"
  ])
  project                    = var.project_id
  service                    = each.key
  disable_dependent_services = false
}

resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-service-account"
  display_name = "Cloud Run Service Account"
}

resource "google_project_iam_member" "cloud_run_registry_access" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_firestore_access" {
  project = var.project_id
  role    = "roles/datastore.user" 
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_cloud_run_service" "file_api" {
  name     = "file-processor-api"
  location = var.region

  template {
    spec {
      containers {
        image = var.api_image
        startup_probe {
          initial_delay_seconds = 10
          timeout_seconds = 30
          period_seconds = 60
          failure_threshold = 3
          tcp_socket {
            port = 8080
          }
        }
      }
      service_account_name = google_service_account.cloud_run_sa.email
    }
  }

  depends_on = [
    google_project_service.services
  ]
  
}

resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.file_api.name
  location = google_cloud_run_service.file_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}


