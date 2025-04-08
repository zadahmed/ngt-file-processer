provider "google" {
    project = var.project_id
    region = var.region 
}

resource "google_storage_bucket" "file_upload_bucket" {
    name = "file-upload-bucket-${var.project_id}"
    location = var.region
    force_destroy = true
    uniform_bucket_level_access = true 
}

resource "google_storage_bucket" "function_code" {
    name = "function-code-bucket-${var.project_id}"
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

resource "google_cloudfunctions_function" "process_file_function" {
  name        = "process-file"
  description = "Function to process files uploaded to bucket"
  runtime     = "python310"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.function_code.name
  source_archive_object = google_storage_bucket_object.function_object.name
  entry_point           = "process_file"
  
  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.file_upload_bucket.name
  }
}


resource "google_cloud_run_service" "file_api" {
  name     = "file-processor-api"
  location = var.region

  template {
    spec {
      containers {
        image = var.api_image
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.file_api.name
  location = google_cloud_run_service.file_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
