#!/usr/bin/env python3
"""
Ultra Simple SecureEye Backend - Just Flask and SocketIO
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
active_cameras = {}
detection_enabled = True

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_cameras': len(active_cameras),
        'version': 'ultra-simple-1.0',
        'message': 'SecureEye Backend is running (ultra simple mode)'
    })

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """Get list of active cameras"""
    return jsonify({
        'cameras': list(active_cameras.keys()),
        'count': len(active_cameras)
    })

@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection"""
    print(f'🔌 Client connected: {request.sid}')
    emit('status', {'message': 'Connected to SecureEye AI backend (ultra simple mode)'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'🔌 Client disconnected: {request.sid}')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start AI detection for a camera"""
    camera_id = data.get('camera_id', 'default_camera')
    
    if camera_id not in active_cameras:
        active_cameras[camera_id] = {
            'stream_url': f'camera_{camera_id}',
            'added_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        emit('detection_started', {'camera_id': camera_id})
        print(f'🎯 AI detection started for camera {camera_id}')
        
        # Start a simple detection simulation
        def simulate_detections():
            count = 0
            while camera_id in active_cameras:
                time.sleep(5)  # Wait 5 seconds
                count += 1
                
                # Simulate detection every 3 cycles
                if count % 3 == 0:
                    detections = {
                        'motion': {
                            'detected': True,
                            'confidence': 0.85,
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                    
                    socketio.emit('detection_alert', {
                        'camera_id': camera_id,
                        'detections': detections,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f'🚨 Detection alert sent for camera {camera_id}')
        
        # Start detection thread
        detection_thread = threading.Thread(target=simulate_detections)
        detection_thread.daemon = True
        detection_thread.start()
    else:
        emit('error', {'message': 'Camera already being monitored'})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop AI detection for a camera"""
    camera_id = data.get('camera_id', 'default_camera')
    
    if camera_id in active_cameras:
        del active_cameras[camera_id]
        emit('detection_stopped', {'camera_id': camera_id})
        print(f'🛑 AI detection stopped for camera {camera_id}')
    else:
        emit('error', {'message': 'Camera not found'})

if __name__ == '__main__':
    print("🚀 Starting SecureEye AI Backend (Ultra Simple Mode)...")
    print("📡 Available endpoints:")
    print("   - GET /api/health - Health check")
    print("   - GET /api/cameras - List cameras")
    print("")
    print("🔌 WebSocket events:")
    print("   - start_detection - Start monitoring camera")
    print("   - stop_detection - Stop monitoring camera")
    print("   - detection_alert - Receive detection alerts")
    print("")
    print("🌐 Server starting on http://localhost:5000")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")
