import hashlib
import uuid 
from datetime import datetime
from google.cloud import storage, firestore 
import functions_framework


try:
    storage_client = storage.Client()
    db = firestore.Client()
except Exception as e:
    print(f"Error: Could not initialize cloud clients: {e}")
    storage_client = None
    db = None

collection_name = 'files'

@functions_framework.cloud_event
def process_file(cloud_event):
    """
    Process a file uploaded to Google Cloud Storage.
    """

    data = cloud_event.data
    bucket_name = data['bucket']
    file_name = data['name']
    content_type = data.get('contentType', '')
    size = int(data.get('size', 0))

    print(f"Processing file: {file_name} in bucket: {bucket_name}")

    file_id = generate_idempotent_id(file_name, bucket_name)

    if file_already_processed(file_id):
        print(f"File {file_name} has already been processed. Skipping.")
        return

    try: 
        metadata = {
            'file_id': file_id,
            'file_name': file_name,
            'bucket_name': bucket_name,
            'content_type': content_type,
            'size': size,
            'timestamp': datetime.utcnow()
        }

        store_file_metadata(file_id, metadata)   

        return "File processed successfully", 200
    except Exception as e:
        print(f"Error processing file: {e}")
        return "Error processing file", 500


def generate_idempotent_id(file_name, bucket_name):
    """ Generate a unique ID for the file based on its name and bucket.
    """

    hash_input = f"{file_name}_{bucket_name}".encode('utf-8')
    hash_object = hashlib.md5(hash_input).hexdigest()

    return str(uuid.UUID(hash_object))

def file_already_processed(file_id):
    """ Check if the file has already been processed by querying Firestore.
    """

    doc_ref = db.collection(collection_name).document(file_id)
    doc = doc_ref.get()

    return doc.exists

def store_file_metadata(file_id, metadata):
    """ Store file metadata in Firestore.
    """

    doc_ref = db.collection(collection_name).document(file_id)
    doc_ref.set(metadata)

    print(f"Stored metadata for file {file_id} in Firestore.")

def delete_file_metadata(file_id):
    """ Delete file metadata from Firestore.
    """

    doc_ref = db.collection(collection_name).document(file_id)
    doc_ref.delete()

    print(f"Deleted metadata for file {file_id} from Firestore.")

def get_file_metadata(file_id):
    """ Retrieve file metadata from Firestore.
    """

    doc_ref = db.collection(collection_name).document(file_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()
    else:
        print(f"No metadata found for file {file_id}.")
        return None