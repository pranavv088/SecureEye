#!/usr/bin/env python3
"""
Robust SecureEye Backend - Handles errors gracefully
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Global variables
active_cameras = {}
detection_threads = {}
detection_enabled = True

# Simple detection simulation
class SimpleDetector:
    def __init__(self):
        self.detection_count = 0
    
    def simulate_detection(self, camera_id):
        """Simulate AI detection for demo purposes"""
        self.detection_count += 1
        
        # Simulate random detections every 10-30 seconds
        if self.detection_count % 3 == 0:  # More frequent for demo
            detections = {}
            
            import random
            if random.random() < 0.4:  # 40% chance of motion
                detections['motion'] = {
                    'detected': True,
                    'confidence': random.uniform(0.7, 0.95),
                    'timestamp': datetime.now().isoformat()
                }
            
            if random.random() < 0.2:  # 20% chance of fire
                detections['fire'] = {
                    'detected': True,
                    'confidence': random.uniform(0.8, 0.95),
                    'timestamp': datetime.now().isoformat()
                }
            
            if detections:
                socketio.emit('detection_alert', {
                    'camera_id': camera_id,
                    'detections': detections,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"🚨 Detection alert sent for camera {camera_id}: {list(detections.keys())}")

# Initialize detector
detector = SimpleDetector()

def process_camera_stream(camera_id, stream_url):
    """Process camera stream for AI detection (simulated)"""
    global detection_enabled
    
    logger.info(f"🎥 Started processing camera {camera_id}")
    
    while detection_enabled and camera_id in active_cameras:
        try:
            # Simulate processing delay
            time.sleep(3)  # Faster for demo
            
            # Run detection simulation
            detector.simulate_detection(camera_id)
        except Exception as e:
            logger.error(f"Error in camera processing: {e}")
            break
    
    logger.info(f"🛑 Stopped processing camera {camera_id}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_cameras': len(active_cameras),
        'version': 'robust-1.0',
        'message': 'SecureEye Backend is running (robust mode)',
        'detection_enabled': detection_enabled
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
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        stream_url = data.get('stream_url')
        
        if not camera_id or not stream_url:
            return jsonify({'error': 'Missing camera_id or stream_url'}), 400
        
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
        
        logger.info(f"📹 Camera {camera_id} added successfully")
        return jsonify({
            'message': 'Camera added successfully',
            'camera_id': camera_id
        })
    except Exception as e:
        logger.error(f"Error adding camera: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cameras/<camera_id>', methods=['DELETE'])
def remove_camera(camera_id):
    """Remove a camera from monitoring"""
    try:
        if camera_id not in active_cameras:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Remove from active cameras
        del active_cameras[camera_id]
        
        # Stop detection thread
        if camera_id in detection_threads:
            del detection_threads[camera_id]
        
        logger.info(f"📹 Camera {camera_id} removed successfully")
        return jsonify({
            'message': 'Camera removed successfully',
            'camera_id': camera_id
        })
    except Exception as e:
        logger.error(f"Error removing camera: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'🔌 Client connected: {request.sid}')
    emit('status', {'message': 'Connected to SecureEye AI backend (robust mode)'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'🔌 Client disconnected: {request.sid}')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start AI detection for a camera"""
    try:
        camera_id = data.get('camera_id', 'default_camera')
        stream_url = data.get('stream_url', f'camera_{camera_id}')
        
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
            logger.info(f'🎯 AI detection started for camera {camera_id}')
        else:
            emit('error', {'message': 'Camera already being monitored'})
    except Exception as e:
        logger.error(f"Error starting detection: {e}")
        emit('error', {'message': str(e)})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop AI detection for a camera"""
    try:
        camera_id = data.get('camera_id', 'default_camera')
        
        if camera_id in active_cameras:
            del active_cameras[camera_id]
            if camera_id in detection_threads:
                del detection_threads[camera_id]
            emit('detection_stopped', {'camera_id': camera_id})
            logger.info(f'🛑 AI detection stopped for camera {camera_id}')
        else:
            emit('error', {'message': 'Camera not found'})
    except Exception as e:
        logger.error(f"Error stopping detection: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("🚀 Starting SecureEye AI Backend (Robust Mode)...")
    print("📡 Available endpoints:")
    print("   - GET /api/health - Health check")
    print("   - GET /api/cameras - List cameras")
    print("   - POST /api/cameras - Add camera")
    print("   - DELETE /api/cameras/<id> - Remove camera")
    print("")
    print("🔌 WebSocket events:")
    print("   - start_detection - Start monitoring camera")
    print("   - stop_detection - Stop monitoring camera")
    print("   - detection_alert - Receive detection alerts")
    print("")
    print("🌐 Server starting on http://localhost:5000")
    print("=" * 60)
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        input("Press Enter to exit...")
