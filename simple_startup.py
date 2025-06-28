#!/usr/bin/env python3
"""
Simple startup script to test basic FastAPI functionality.
This will help identify if the issue is with the app itself or with dependencies.
"""

import os
import sys
import logging
import uvicorn
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_minimal_app():
    """Create a minimal FastAPI app for testing."""
    app = FastAPI(title="Minimal Test App", version="0.1.0")
    
    @app.get("/")
    def read_root():
        return {"status": "Minimal app working", "message": "Hello from minimal FastAPI app"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "minimal": True}
    
    return app

def main():
    """Start the minimal app."""
    logger.info("🚀 Starting minimal FastAPI app...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"PORT environment variable: {os.getenv('PORT', 'not set')}")
    
    try:
        app = create_minimal_app()
        logger.info("✅ Minimal app created successfully")
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 8080))
        logger.info(f"Starting uvicorn on port {port}")
        
        # Start the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Error starting minimal app: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 