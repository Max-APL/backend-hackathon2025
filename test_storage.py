#!/usr/bin/env python3
"""
Test script to verify Firebase Storage is working correctly.
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

def test_storage_bucket():
    """Test Firebase Storage bucket access."""
    logger.info("Testing Firebase Storage bucket...")
    
    try:
        import firebase_admin
        from firebase_admin import storage
        
        # Get the storage bucket
        bucket = storage.bucket()
        logger.info(f"✅ Storage bucket accessed: {bucket.name}")
        
        # List a few files (if any exist)
        blobs = list(bucket.list_blobs(max_results=5))
        logger.info(f"✅ Found {len(blobs)} files in bucket")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Storage bucket test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_storage_service():
    """Test storage service functionality."""
    logger.info("Testing storage service...")
    
    try:
        from app.services.storage_service import storage_service
        
        if storage_service._initialized:
            logger.info("✅ Storage service is initialized")
            
            # Test image_exists method
            exists = storage_service.image_exists("test_file.jpg")
            logger.info(f"✅ image_exists test completed: {exists}")
            
            return True
        else:
            logger.error("❌ Storage service is not initialized")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage service test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_firebase_config():
    """Test Firebase config initialization."""
    logger.info("Testing Firebase config...")
    
    try:
        from app.core.firebase_config import firebase_config
        
        # Test initialization
        firebase_config.initialize()
        
        if firebase_config._initialized:
            logger.info("✅ Firebase config initialized successfully")
            
            # Test storage bucket access
            bucket = firebase_config.storage_bucket
            logger.info(f"✅ Storage bucket accessed via config: {bucket.name}")
            
            return True
        else:
            logger.error("❌ Firebase config not initialized")
            return False
            
    except Exception as e:
        logger.error(f"❌ Firebase config test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Firebase Storage tests...")
    
    tests = [
        test_storage_bucket,
        test_storage_service,
        test_firebase_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        logger.info("")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All Firebase Storage tests passed!")
        return 0
    else:
        logger.error("❌ Some Firebase Storage tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 