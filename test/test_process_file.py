import os
import sys
from unittest.mock import patch, MagicMock
import pytest
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

mock_storage = MagicMock()
mock_db = MagicMock()

with patch('google.cloud.storage.Client', return_value=mock_storage):
    with patch('google.cloud.firestore.Client', return_value=mock_db):
        import main

class CloudEvent:
    def __init__(self, data):
        self.data = data

@pytest.fixture
def event_data():
    return {
        "bucket": "ngt-test-bucket",
        "name": "ngt-test-file.txt",
        "contentType": "text/plain",
        "size": 1024
    }

@pytest.fixture
def cloud_event(event_data):
    return CloudEvent(event_data)

@pytest.fixture
def mock_firestore():
    with patch.object(main, 'db') as mock_db:
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        mock_doc = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        yield mock_db, mock_doc_ref, mock_doc

@pytest.fixture
def mock_storage():
    with patch.object(main, 'storage_client') as mock_storage:
        yield mock_storage

def test_ngt_process_file_new_file(cloud_event, mock_firestore, mock_storage):
    _, mock_doc_ref, mock_doc = mock_firestore
    mock_doc.exists = False
    
    result = main.process_file(cloud_event)
    
    assert result[0] == "File processed successfully"
    assert result[1] == 200
    mock_doc_ref.set.assert_called_once()

def test_ngt_process_file_existing_file(cloud_event, mock_firestore, mock_storage):
    _, mock_doc_ref, mock_doc = mock_firestore
    mock_doc.exists = True
    
    result = main.process_file(cloud_event)
    
    assert result is None
    mock_doc_ref.set.assert_not_called()

def test_ngt_generate_idempotent_id():
    file_name = "ngt-test-file.txt"
    bucket_name = "ngt-test-bucket"

    id1 = main.generate_idempotent_id(file_name, bucket_name)
    id2 = main.generate_idempotent_id(file_name, bucket_name)
    
    assert id1 == id2
    assert uuid.UUID(id1)

def test_ngt_file_already_processed(mock_firestore):
    _, _, mock_doc = mock_firestore
    mock_doc.exists = True
    assert main.file_already_processed("ngt-test-id") is True
    
    mock_doc.exists = False
    assert main.file_already_processed("ngt-test-id") is False

def test_ngt_store_file_metadata(mock_firestore):
    mock_db, mock_doc_ref, _ = mock_firestore
    file_id = "ngt-test-id"
    metadata = {'file_id': file_id, 'file_name': 'ngt-test-file.txt'}
    
    main.store_file_metadata(file_id, metadata)
    
    mock_doc_ref.set.assert_called_once_with(metadata)

def test_ngt_get_file_metadata(mock_firestore):
    _, _, mock_doc = mock_firestore
    mock_doc.exists = True
    test_data = {'file_name': 'ngt-test-file.txt'}
    mock_doc.to_dict.return_value = test_data
    
    result = main.get_file_metadata("ngt-test-id")
    
    assert result == test_data

def test_ngt_delete_file_metadata(mock_firestore):
    mock_db, mock_doc_ref, _ = mock_firestore
    main.delete_file_metadata("ngt-test-id")
    mock_doc_ref.delete.assert_called_once()

def test_ngt_process_file_error_handling(cloud_event, mock_firestore):
    _, mock_doc_ref, mock_doc = mock_firestore
    mock_doc_ref.set.side_effect = Exception("NGT test exception")
    mock_doc.exists = False

    result = main.process_file(cloud_event)
    
    assert result[0] == "Error processing file"
    assert result[1] == 500