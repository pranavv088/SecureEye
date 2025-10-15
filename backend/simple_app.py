#!/usr/bin/env python3
"""
Simplified SecureEye Backend
This version works without heavy AI dependencies for quick testing
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
active_cameras = {}
detection_threads = {}
detection_enabled = True

# Simple detection simulation (without OpenCV)
class SimpleDetector:
    def __init__(self):
        self.detection_threshold = 0.7
        self.mock_detections = ['fire', 'motion', 'violence', 'crowd']
    
    def simulate_detection(self, camera_id):
        """Simulate AI detection for testing"""
        import random
        
        # Randomly generate detections
        if random.random() > 0.8:  # 20% chance of detection
            detection_type = random.choice(self.mock_detections)
            confidence = random.uniform(0.6, 0.95)
            
            return {
                'detected': True,
                'type': detection_type,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
        return None

# Initialize detector
detector = SimpleDetector()

def process_camera_stream(camera_id, stream_url):
    """Process camera stream for AI detection (simulated)"""
    global detection_enabled
    
    print(f"Started processing camera {camera_id}")
    
    while detection_enabled and camera_id in active_cameras:
        # Simulate detection processing
        detection = detector.simulate_detection(camera_id)
        
        if detection:
            # Send detection via WebSocket
            socketio.emit('detection_alert', {
                'camera_id': camera_id,
                'detection_type': detection['type'],
                'confidence': detection['confidence'],
                'timestamp': detection['timestamp']
            })
            print(f"Detection: {detection['type']} on camera {camera_id}")
        
        # Small delay to prevent overwhelming
        time.sleep(2)  # Check every 2 seconds
    
    print(f"Stopped processing camera {camera_id}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_cameras': len(active_cameras),
        'mode': 'simulation'
    })

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """Get list of active cameras"""
    return jsonify({
        'cameras': list(active_cameras.keys()),
        'count': len(active_cameras)
    })

@app.route('/api/cameras', methods=['POST'])
def add_camera():
    """Add a new camera for monitoring"""
    data = request.get_json()
    camera_id = data.get('camera_id', f'camera_{len(active_cameras) + 1}')
    stream_url = data.get('stream_url', f'stream_{camera_id}')
    
    if camera_id in active_cameras:
        return jsonify({'error': 'Camera already exists'}), 400
    
    # Add camera to active list
    active_cameras[camera_id] = {
        'stream_url': stream_url,
        'added_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    # Start detection thread
    detection_thread = threading.Thread(
        target=process_camera_stream,
        args=(camera_id, stream_url)
    )
    detection_thread.daemon = True
    detection_thread.start()
    detection_threads[camera_id] = detection_thread
    
    return jsonify({
        'message': 'Camera added successfully',
        'camera_id': camera_id
    })

@app.route('/api/cameras/<camera_id>', methods=['DELETE'])
def remove_camera(camera_id):
    """Remove a camera from monitoring"""
    if camera_id not in active_cameras:
        return jsonify({'error': 'Camera not found'}), 404
    
    # Remove from active cameras
    del active_cameras[camera_id]
    
    # Stop detection thread
    if camera_id in detection_threads:
        del detection_threads[camera_id]
    
    return jsonify({
        'message': 'Camera removed successfully',
        'camera_id': camera_id
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('status', {'message': 'Connected to SecureEye backend (simulation mode)'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start AI detection for a camera"""
    camera_id = data.get('camera_id', f'camera_{len(active_cameras) + 1}')
    stream_url = data.get('stream_url', f'stream_{camera_id}')
    
    if camera_id not in active_cameras:
        active_cameras[camera_id] = {
            'stream_url': stream_url,
            'added_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        detection_thread = threading.Thread(
            target=process_camera_stream,
            args=(camera_id, stream_url)
        )
        detection_thread.daemon = True
        detection_thread.start()
        detection_threads[camera_id] = detection_thread
        
        emit('detection_started', {'camera_id': camera_id})
    else:
        emit('error', {'message': 'Camera already being monitored'})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop AI detection for a camera"""
    camera_id = data.get('camera_id')
    
    if camera_id in active_cameras:
        del active_cameras[camera_id]
        if camera_id in detection_threads:
            del detection_threads[camera_id]
        emit('detection_stopped', {'camera_id': camera_id})
    else:
        emit('error', {'message': 'Camera not found'})

if __name__ == '__main__':
    print("Starting SecureEye Backend (Simplified Mode)...")
    print("=" * 50)
    print("Features:")
    print("- Flask REST API")
    print("- WebSocket communication")
    print("- Simulated AI detection")
    print("- Camera management")
    print("=" * 50)
    print("Available endpoints:")
    print("- GET /api/health - Health check")
    print("- GET /api/cameras - List cameras")
    print("- POST /api/cameras - Add camera")
    print("- DELETE /api/cameras/<id> - Remove camera")
    print("\nWebSocket events:")
    print("- start_detection - Start monitoring camera")
    print("- stop_detection - Stop monitoring camera")
    print("- detection_alert - Receive detection alerts")
    print("\nServer starting on http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
