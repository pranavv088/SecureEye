#!/usr/bin/env python3
"""
Minimal SecureEye Backend
Ultra-simple version for testing
"""

from flask import Flask, jsonify
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'SecureEye Backend is running!',
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy'
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Backend is running in minimal mode'
    })

@app.route('/api/cameras')
def cameras():
    """Get cameras endpoint"""
    return jsonify({
        'cameras': [],
        'count': 0,
        'message': 'No cameras configured in minimal mode'
    })

if __name__ == '__main__':
    print("Starting SecureEye Minimal Backend...")
    print("Server will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  GET / - Home")
    print("  GET /api/health - Health check")
    print("  GET /api/cameras - List cameras")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
