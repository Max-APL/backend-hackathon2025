#!/usr/bin/env python3
"""
Test script to verify that the FastAPI application can start without issues.
This helps identify any import or configuration problems before deployment.
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported."""
    logger.info("Testing imports...")
    
    try:
        import fastapi
        logger.info("✅ FastAPI imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import FastAPI: {e}")
        return False
    
    try:
        import firebase_admin
        logger.info("✅ Firebase Admin imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import Firebase Admin: {e}")
        return False
    
    try:
        from app.app import app
        logger.info("✅ Main app imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import main app: {e}")
        return False
    
    try:
        from app.api.v1.api_router import api_router
        logger.info("✅ API router imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import API router: {e}")
        return False
    
    return True

def test_app_creation():
    """Test that the FastAPI app can be created."""
    logger.info("Testing app creation...")
    
    try:
        from app.app import app
        logger.info("✅ FastAPI app created successfully")
        logger.info(f"   - Title: {app.title}")
        logger.info(f"   - Version: {app.version}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create FastAPI app: {e}")
        return False

def test_routes():
    """Test that routes can be registered."""
    logger.info("Testing route registration...")
    
    try:
        from app.app import app
        routes = [route.path for route in app.routes]
        logger.info(f"✅ Routes registered successfully: {len(routes)} routes found")
        for route in routes[:5]:  # Show first 5 routes
            logger.info(f"   - {route}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to register routes: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting startup tests...")
    
    tests = [
        test_imports,
        test_app_creation,
        test_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        logger.info("")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All tests passed! The application should start successfully.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please fix the issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 