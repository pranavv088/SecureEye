#!/usr/bin/env python3
"""
SecureEye Setup Test Script
This script tests the basic setup and dependencies
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if required packages can be imported"""
    required_packages = [
        'flask', 'flask_socketio', 'opencv-python', 
        'tensorflow', 'torch', 'numpy', 'pillow',
        'firebase-admin', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'flask_socketio':
                import flask_socketio
            elif package == 'firebase-admin':
                import firebase_admin
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r backend/requirements.txt")
        return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'backend/app.py',
        'backend/requirements.txt',
        'backend/env_template.txt',
        'firebase-config.js',
        'home.html',
        'landing.html',
        'login.html',
        'signup.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    return True

def check_firebase_config():
    """Check Firebase configuration"""
    try:
        with open('firebase-config.js', 'r') as f:
            content = f.read()
            
        if 'eye-61167' in content:
            print("✅ Firebase configuration found")
            return True
        else:
            print("❌ Firebase configuration not found")
            return False
    except FileNotFoundError:
        print("❌ firebase-config.js not found")
        return False

def check_camera_access():
    """Check if camera access is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera access available")
            cap.release()
            return True
        else:
            print("❌ Camera access not available")
            return False
    except ImportError:
        print("❌ OpenCV not installed")
        return False

def main():
    """Main test function"""
    print("🔍 SecureEye Setup Test")
    print("=" * 40)
    
    tests = [
        ("Python Version", check_python_version),
        ("Required Files", check_files),
        ("Firebase Config", check_firebase_config),
        ("Dependencies", check_dependencies),
        ("Camera Access", check_camera_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! SecureEye is ready to run.")
        print("\nNext steps:")
        print("1. Configure Firebase service account in backend/firebase-service-account.json")
        print("2. Update backend/.env with your credentials")
        print("3. Run backend: python backend/app.py")
        print("4. Serve frontend: python -m http.server 8000")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nSetup help:")
        print("- Install Python 3.8+: https://python.org")
        print("- Install dependencies: pip install -r backend/requirements.txt")
        print("- Check Firebase configuration")

if __name__ == "__main__":
    main()
