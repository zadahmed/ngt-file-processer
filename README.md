# NGT File Processor Cloud Function

This repository contains a Google Cloud Function that processes files uploaded to Google Cloud Storage and stores metadata in Firestore. The solution was built for the Next Gate Tech (NGT) Software Engineer assignment.

## Project Structure

```
.
├── main.py           # Cloud Function code
├── requirements.txt  # Python dependencies
├── api/              # API service for file metadata
├── test/             # Test files
└── .venv/            # Virtual environment (not tracked in git)
```

## Cloud Function

The Cloud Function (`main.py`) is triggered when files are uploaded to a Cloud Storage bucket. It extracts file metadata and stores it in Firestore, ensuring idempotent processing even if the function is triggered multiple times for the same file.

## Deployment

Deployed the Cloud Function using Google Cloud CLI:

```bash
gcloud functions deploy process-file \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_file \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=NGT_BUCKET" \
  --memory=256MB \
  --timeout=60s
```

## Testing

For local development:

1. Set up a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run tests:
   ```bash
   pytest test/
   ```

## API Service

The `api/` directory contains a FastAPI service that provides endpoints to:

- List processed files
- Get file metadata
- Download files
- Delete files

The API service is deployed separately as a Cloud Run service.
