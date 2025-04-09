import logging
from google.cloud import firestore
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache()
def get_db():
    """
    Initialize Firestore client and return the database instance.
    """
    try:
        db = firestore.Client()
        logger.info("Firestore client initialized successfully.")
        return db
    except Exception as e:
        logger.error(f"Error initializing Firestore client: {e}")
        return None