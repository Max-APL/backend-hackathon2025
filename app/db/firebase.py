import os
import firebase_admin
from firebase_admin import credentials, firestore

firebase_app = None
db = None

def get_firestore():
    global firebase_app, db
    if not firebase_admin._apps:
        cred_path = os.path.join(os.getcwd(), "hackaton-a44c8-firebase-adminsdk-fbsvc-9e2a2b3314.json")
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred)
        db = firestore.client()
    return db
