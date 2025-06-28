#!/usr/bin/env python3
"""
Minimal startup script to debug container startup issues.
This script will help identify what's preventing the FastAPI app from starting.
"""

import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test basic Python imports."""
    logger.info("Testing basic imports...")
    
    try:
        import fastapi
        logger.info("✅ FastAPI imported successfully")
    except Exception as e:
        logger.error(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        logger.info("✅ Uvicorn imported successfully")
    except Exception as e:
        logger.error(f"❌ Uvicorn import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test FastAPI app creation."""
    logger.info("Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Test App")
        logger.info("✅ FastAPI app created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ FastAPI app creation failed: {e}")
        return False

def test_app_import():
    """Test importing the main app."""
    logger.info("Testing main app import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app.app import app
        logger.info("✅ Main app imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Main app import failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_uvicorn_startup():
    """Test if uvicorn can start the app."""
    logger.info("Testing uvicorn startup...")
    
    try:
        import uvicorn
        from app.app import app
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 8080))
        logger.info(f"Starting uvicorn on port {port}")
        
        # Start uvicorn in a way that we can control
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        logger.info("✅ Uvicorn server configured successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Uvicorn startup failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all startup tests."""
    logger.info("🚀 Starting startup debug tests...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Environment variables: PORT={os.getenv('PORT', 'not set')}")
    
    tests = [
        test_basic_imports,
        test_app_creation,
        test_app_import,
        test_uvicorn_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Test {test.__name__} crashed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info("")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All tests passed! The application should start successfully.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 