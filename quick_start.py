#!/usr/bin/env python3
"""
SecureEye Quick Start Script
Starts the backend server and provides instructions for frontend
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if we're in the right directory
    if not os.path.exists('backend/app.py'):
        print("❌ Please run this script from the SecureEye project root directory")
        return False
    
    # Check if Python is available
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    return True

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting SecureEye Backend...")
    
    backend_dir = Path('backend')
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Check if virtual environment exists
        venv_path = backend_dir / 'venv'
        if venv_path.exists():
            print("✅ Virtual environment found")
            
            # Activate virtual environment and start server
            if os.name == 'nt':  # Windows
                python_exe = venv_path / 'Scripts' / 'python.exe'
                pip_exe = venv_path / 'Scripts' / 'pip.exe'
            else:  # Linux/Mac
                python_exe = venv_path / 'bin' / 'python'
                pip_exe = venv_path / 'bin' / 'pip'
            
            # Install dependencies if needed
            print("📦 Checking dependencies...")
            try:
                subprocess.run([str(pip_exe), 'list'], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print("📦 Installing dependencies...")
                subprocess.run([str(pip_exe), 'install', '-r', 'requirements.txt'], cwd=backend_dir)
            
            # Start the server
            print("🌐 Starting backend server on http://localhost:5000")
            return subprocess.Popen([str(python_exe), 'app.py'], cwd=backend_dir)
            
        else:
            print("❌ Virtual environment not found. Please run setup first:")
            print("   Windows: backend\\setup.bat")
            print("   Linux/Mac: cd backend && ./setup.sh")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("\n🌐 Starting Frontend Server...")
    
    try:
        # Start Python HTTP server
        print("📡 Starting HTTP server on http://localhost:8000")
        return subprocess.Popen([sys.executable, '-m', 'http.server', '8000'])
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False

def main():
    """Main function"""
    print("🎯 SecureEye Quick Start")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("❌ Failed to start backend")
            sys.exit(1)
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Failed to start frontend")
            backend_process.terminate()
            sys.exit(1)
        
        # Wait a moment for frontend to start
        time.sleep(2)
        
        print("\n🎉 SecureEye is running!")
        print("=" * 50)
        print("📱 Frontend: http://localhost:8000")
        print("🔧 Backend:  http://localhost:5000")
        print("🧪 Test Page: http://localhost:8000/test.html")
        print("\n📋 Next Steps:")
        print("1. Open your browser and go to http://localhost:8000")
        print("2. Create an account or sign in")
        print("3. Allow camera access when prompted")
        print("4. Start AI detection on your cameras")
        print("\n⚠️  Important Notes:")
        print("- Make sure to configure Firebase credentials in backend/.env")
        print("- Ensure your camera is connected and working")
        print("- Check the test page for setup verification")
        print("\n🛑 Press Ctrl+C to stop both servers")
        
        # Try to open browser
        try:
            time.sleep(3)
            webbrowser.open('http://localhost:8000')
        except:
            pass
        
        # Wait for user to stop
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down SecureEye...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
