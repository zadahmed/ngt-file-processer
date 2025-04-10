# NGT File Processing System

A cloud-based system for processing files uploaded to a storage bucket and providing API access to the processed data.


API Url - https://file-processor-api-797926948558.us-central1.run.app

## Overview

This project implements a complete file processing system using Google Cloud Platform services:

1. **Storage Bucket**: For uploading files to be processed
2. **Cloud Function**: Triggered when files are uploaded, processes them, and stores metadata in Firestore
3. **FastAPI Service**: Deployed on Cloud Run to provide CRUD operations for the processed file metadata
4. **Infrastructure as Code**: Uses Terraform to provision and manage the entire infrastructure

## Components

### Cloud Function

The Cloud Function is triggered when files are uploaded to the storage bucket. It:
- Extracts file metadata (name, type, size, etc.)
- Generates a unique ID for each file to ensure idempotent processing
- Stores the metadata in Firestore
- Handles concurrent file uploads efficiently

### API Service

A FastAPI application that provides CRUD operations for accessing file metadata:
- List all processed files
- Get details for a specific file
- Update file metadata
- Delete file records


### Infrastructure

Terraform is used to provision all required infrastructure:
- Storage buckets
- Cloud Function
- Cloud Run service
- IAM permissions
- Service accounts

## Getting Started

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://www.terraform.io/downloads.html)
- [Python 3.11+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/zadahmed/ngt-file-processer
   cd file-processing-system
   ```

2. Run the API locally:
   ```bash
   cd api
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. Visit http://localhost:8000/docs to see the API documentation

### Deployment

1. Build and push the API container:
   ```bash
   cd api
   docker build -t gcr.io/ngt-file-processor/file-processor-api:latest --platform linux/amd64 .
   gcloud auth configure-docker
   docker push gcr.io/ngt-file-processor/file-processor-api:latest
   ```

2. Deploy with Terraform:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```



## Usage

### Uploading Files

Upload files to the storage bucket:
```bash
gsutil cp random.txt gs://file-upload-bucket-YOUR-PROJECT-ID/
```

### Using the API

Access the API using the Cloud Run URL:
```bash
API_URL=https://file-processor-api-797926948558.us-central1.run.app

curl $API_URL/files

curl $API_URL/files/file-id
```

