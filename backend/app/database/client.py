import firebase_admin
from firebase_admin import credentials, firestore
from app.config import settings

_client = None

def get_firestore_client():
    global _client
    if _client is None:
        cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS) if settings.GOOGLE_APPLICATION_CREDENTIALS else None
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        _client = firestore.client()
    return _client
