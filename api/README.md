# File Processor API

A FastAPI-based API for accessing and managing file metadata stored in Firestore.

## Getting Started

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at http://localhost:8000/docs

### Running Tests

1. Run tests with coverage:
   ```bash
   pytest --cov=app
   ```

### Docker

1. Build the Docker image:
   ```bash
   docker build -t file-processor-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 file-processor-api
   ```

## API Endpoints

- `GET /files` - List all files
- `GET /files/{file_id}` - Get a specific file
- `PUT /files/{file_id}` - Update file metadata
- `DELETE /files/{file_id}` - Delete file metadata
- `GET /health` - Health check endpoint

## Deployment

Run locally

```bash
docker run -p 8080:8080 gcr.io/ngt-file-processor/file-processor-api
```

Deploy to Cloud Run:

```bash
docker build -t gcr.io/ngt-file-processor/file-processor-api:latest .

gcloud auth configure-docker
docker push gcr.io/ngt-file-processor/file-processor-api

gcloud run deploy file-processor-api \
  --image gcr.io/ngt-file-processor/file-processor-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```
