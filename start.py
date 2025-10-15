#!/usr/bin/env python3
"""
SecureEye Production Startup
Clean startup for production deployment
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the backend server"""
    print("🚀 Starting SecureEye Backend...")
    backend_path = Path("backend")
    venv_python = backend_path / "venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("❌ Backend virtual environment not found!")
        return False
    
    try:
        backend_process = subprocess.Popen([
            str(venv_python), 
            str(backend_path / "app.py")
        ], cwd=backend_path)
        
        print("✅ Backend started")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting SecureEye Frontend...")
    
    try:
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "8000"
        ])
        
        print("✅ Frontend started")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main startup function"""
    print("🎯 SecureEye Production Startup")
    print("=" * 40)
    
    # Start backend
    if not start_backend():
        return
    
    # Start frontend
    if not start_frontend():
        return
    
    # Wait for servers to start
    print("⏳ Initializing servers...")
    time.sleep(3)
    
    print("\n🎉 SecureEye is running!")
    print("\n📱 Access URLs:")
    print("- Dashboard: http://localhost:8000/home.html")
    print("- Test Page: http://localhost:8000/test.html")
    print("\nPress Ctrl+C to stop servers")

if __name__ == "__main__":
    try:
        main()
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping SecureEye...")
        print("✅ Servers stopped")
