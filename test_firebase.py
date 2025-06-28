#!/usr/bin/env python3
"""
Test script to verify Firebase initialization works correctly.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_firebase_initialization():
    """Test Firebase initialization."""
    logger.info("Testing Firebase initialization...")
    
    try:
        # Test basic imports
        import firebase_admin
        from firebase_admin import credentials, firestore
        logger.info("✅ Firebase Admin imports successful")
        
        # Test app initialization
        try:
            app = firebase_admin.get_app()
            logger.info("✅ Firebase app already exists")
        except ValueError:
            logger.info("🔄 Initializing Firebase app...")
            
            # Check if credentials file exists
            cred_file = "hackaton-a44c8-f3d9ad76a54d.json"
            if os.path.exists(cred_file):
                logger.info(f"📁 Using local credentials: {cred_file}")
                cred = credentials.Certificate(cred_file)
                firebase_admin.initialize_app(cred)
            else:
                logger.info("☁️ Using Application Default Credentials")
                firebase_admin.initialize_app()
            
            logger.info("✅ Firebase app initialized successfully")
        
        # Test Firestore client
        db = firestore.client()
        logger.info("✅ Firestore client created successfully")
        
        # Test basic Firestore operation
        doc_ref = db.collection("test").document("test")
        doc_ref.set({"test": "data"})
        doc = doc_ref.get()
        if doc.exists:
            logger.info("✅ Firestore read/write test successful")
        else:
            logger.error("❌ Firestore read/write test failed")
            return False
        
        # Clean up test document
        doc_ref.delete()
        logger.info("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Firebase test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_storage_service():
    """Test storage service initialization."""
    logger.info("Testing storage service...")
    
    try:
        from app.services.storage_service import storage_service
        logger.info("✅ Storage service imported successfully")
        
        if storage_service._initialized:
            logger.info("✅ Storage service initialized successfully")
            return True
        else:
            logger.warning("⚠️ Storage service not initialized")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage service test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Firebase tests...")
    
    tests = [
        test_firebase_initialization,
        test_storage_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        logger.info("")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All Firebase tests passed!")
        return 0
    else:
        logger.error("❌ Some Firebase tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 