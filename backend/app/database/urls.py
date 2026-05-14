try:
    from google.cloud import firestore
except ImportError:
    firestore = None

try:
    from google.cloud.firestore_v1 import Increment
except ImportError:
    try:
        from google.cloud.firestore import Increment
    except ImportError:
        Increment = None

from app.database.client import get_firestore_client

try:
    from google.api_core.exceptions import Conflict, NotFound
except ImportError:
    Conflict = Exception
    NotFound = Exception

def create_url_entry(short_code: str, long_url: str, api_key: str) -> None:
    db = get_firestore_client()
    doc_ref = db.collection('urls').document(short_code)
    server_timestamp = firestore.SERVER_TIMESTAMP if firestore is not None else None
    doc_ref.create({
        'long_url': long_url,
        'api_key': api_key,
        'created_at': server_timestamp,
        'clicks': 0,
    })

def get_url_entry(short_code: str) -> dict:
    db = get_firestore_client()
    doc = db.collection('urls').document(short_code).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data['short_code'] = doc.id
    return data

def increment_clicks(short_code: str) -> None:
    db = get_firestore_client()
    doc_ref = db.collection('urls').document(short_code)
    doc_ref.update({'clicks': Increment(1)})

def delete_url_entry(short_code: str) -> None:
    db = get_firestore_client()
    db.collection('urls').document(short_code).delete()
