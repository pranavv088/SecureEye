#!/usr/bin/env python3
"""
SecureEye Backend with Real Human Detection
Uses OpenCV Haar cascades for human detection (no TensorFlow required)
"""

import os
import cv2
import numpy as np
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import base64
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
active_cameras = {}
detection_threads = {}
detection_enabled = True
camera_zones = {}  # Store zones for each camera

class HumanDetector:
    def __init__(self):
        """Initialize human detection using OpenCV Haar cascades"""
        try:
            # Load Haar cascade for human detection
            self.human_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
            self.person_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
            
            # If fullbody cascade is not available, try alternative
            if self.human_cascade.empty():
                print("⚠️ Full body cascade not found, using upper body cascade")
                self.human_cascade = self.person_cascade
            
            print("✅ Human detection cascades loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading detection cascades: {e}")
            self.human_cascade = None
            self.person_cascade = None
    
    def detect_humans(self, frame):
        """Detect humans in the frame using Haar cascades"""
        try:
            if self.human_cascade is None:
                return False, 0, []
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect humans
            humans = self.human_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Also try upper body detection for better coverage
            if self.person_cascade is not None:
                upper_bodies = self.person_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Combine detections
                all_detections = list(humans) + list(upper_bodies)
                humans = np.array(all_detections)
            
            if len(humans) > 0:
                return True, len(humans), humans
            else:
                return False, 0, []
                
        except Exception as e:
            print(f"Human detection error: {e}")
            return False, 0, []
    
    def detect_motion(self, frame, previous_frame):
        """Detect motion between frames"""
        try:
            if previous_frame is None:
                return False, 0
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(gray1, gray2)
            
            # Apply threshold
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_area = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area threshold
                    motion_area += area
            
            return motion_area > 1000, motion_area
            
        except Exception as e:
            print(f"Motion detection error: {e}")
            return False, 0

# Initialize detector
detector = HumanDetector()

def process_camera_stream(camera_id, stream_url):
    """Process camera stream for human detection with zone support"""
    global detection_enabled
    
    print(f"🎥 Starting human detection for camera {camera_id}")
    
    # Try multiple camera sources
    cap = None
    camera_sources = []
    
    # Add different camera sources to try
    if stream_url.isdigit():
        camera_sources.append(int(stream_url))
    elif stream_url.startswith('http'):
        camera_sources.append(stream_url)
    else:
        # Try default cameras
        camera_sources.extend([0, 1, 2])  # Try cameras 0, 1, 2
    
    # Try to open camera from different sources
    for source in camera_sources:
        print(f"🔍 Trying camera source: {source}")
        cap = cv2.VideoCapture(source)
        
        # Test if camera works by trying to read a frame
        if cap.isOpened():
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"✅ Camera {camera_id} opened successfully from source {source}")
                break
            else:
                cap.release()
                cap = None
        else:
            cap.release()
            cap = None
    
    if cap is None or not cap.isOpened():
        print(f"❌ Failed to open any camera for {camera_id}")
        # Send error notification
        socketio.emit('camera_error', {
            'camera_id': camera_id,
            'error': 'No accessible camera found',
            'timestamp': datetime.now().isoformat()
        })
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    previous_frame = None
    frame_count = 0
    consecutive_failures = 0
    max_failures = 10
    
    # Get detection zone for this camera (default if not set)
    detection_zone = camera_zones.get(camera_id, {
        'x': 100,      # Left edge of zone
        'y': 100,      # Top edge of zone  
        'width': 400,  # Width of zone
        'height': 300  # Height of zone
    })
    
    while detection_enabled and camera_id in active_cameras:
        ret, frame = cap.read()
        if not ret or frame is None:
            consecutive_failures += 1
            print(f"❌ Failed to read frame from camera {camera_id} (attempt {consecutive_failures})")
            
            if consecutive_failures >= max_failures:
                print(f"❌ Too many failures, stopping camera {camera_id}")
                socketio.emit('camera_error', {
                    'camera_id': camera_id,
                    'error': 'Camera stopped responding',
                    'timestamp': datetime.now().isoformat()
                })
                break
            
            time.sleep(0.5)
            continue
        
        # Reset failure counter on successful read
        consecutive_failures = 0
        
        # Resize frame for processing
        frame = cv2.resize(frame, (640, 480))
        frame_count += 1
        
        # Run detection every 3 frames to reduce CPU load
        if frame_count % 3 == 0:
            detections = {}
            
            # Extract detection zone from frame
            zone_frame = frame[detection_zone['y']:detection_zone['y']+detection_zone['height'],
                              detection_zone['x']:detection_zone['x']+detection_zone['width']]
            
            # Human detection in the zone
            humans_detected, human_count, human_boxes = detector.detect_humans(zone_frame)
            if humans_detected:
                detections['human'] = {
                    'detected': True,
                    'confidence': min(human_count * 0.3, 1.0),
                    'count': human_count,
                    'zone': detection_zone,
                    'timestamp': datetime.now().isoformat()
                }
                print(f"👤 Detected {human_count} human(s) in detection zone of camera {camera_id}")
                
                # Send beep notification
                socketio.emit('zone_alert', {
                    'camera_id': camera_id,
                    'alert_type': 'human_detected',
                    'count': human_count,
                    'confidence': detections['human']['confidence'],
                    'zone': detection_zone,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Motion detection in the zone
            zone_previous = None
            if previous_frame is not None:
                zone_previous = previous_frame[detection_zone['y']:detection_zone['y']+detection_zone['height'],
                                             detection_zone['x']:detection_zone['x']+detection_zone['width']]
            
            motion_detected, motion_area = detector.detect_motion(zone_frame, zone_previous)
            if motion_detected:
                detections['motion'] = {
                    'detected': True,
                    'confidence': min(motion_area / 10000, 1.0),
                    'area': motion_area,
                    'zone': detection_zone,
                    'timestamp': datetime.now().isoformat()
                }
                print(f"🏃 Motion detected in zone of camera {camera_id} (area: {motion_area})")
            
            # Send detections via WebSocket
            if detections:
                socketio.emit('detection_alert', {
                    'camera_id': camera_id,
                    'detections': detections,
                    'timestamp': datetime.now().isoformat(),
                    'zone_based': True
                })
                print(f"🚨 Zone detection alert sent for camera {camera_id}: {list(detections.keys())}")
        
        previous_frame = frame.copy()
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.1)
    
    if cap:
        cap.release()
    print(f"🛑 Stopped human detection for camera {camera_id}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_cameras': len(active_cameras),
        'version': 'human-detection-1.0',
        'message': 'SecureEye Backend with Human Detection is running'
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
    camera_id = data.get('camera_id')
    stream_url = data.get('stream_url', '0')  # Default to camera 0
    
    if not camera_id:
        return jsonify({'error': 'Missing camera_id'}), 400
    
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
    print(f'🔌 Client connected: {request.sid}')
    emit('status', {'message': 'Connected to SecureEye Human Detection backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'🔌 Client disconnected: {request.sid}')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start human detection for a camera with zone monitoring"""
    camera_id = data.get('camera_id')
    stream_url = data.get('stream_url', '0')  # Default to camera 0
    
    if camera_id:
        if camera_id not in active_cameras:
            active_cameras[camera_id] = {
                'stream_url': stream_url,
                'added_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Start real camera detection with zone monitoring
            detection_thread = threading.Thread(
                target=process_camera_stream,
                args=(camera_id, stream_url)
            )
            detection_thread.daemon = True
            detection_thread.start()
            detection_threads[camera_id] = detection_thread
            emit('detection_started', {'camera_id': camera_id, 'mode': 'zone_detection'})
            print(f'🎯 Zone-based human detection started for camera {camera_id}')
        else:
            emit('error', {'message': 'Camera already being monitored'})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop human detection for a camera"""
    camera_id = data.get('camera_id')
    
    if camera_id in active_cameras:
        del active_cameras[camera_id]
        if camera_id in detection_threads:
            del detection_threads[camera_id]
        emit('detection_stopped', {'camera_id': camera_id})
        print(f'🛑 Human detection stopped for camera {camera_id}')
    else:
        emit('error', {'message': 'Camera not found'})

@socketio.on('update_zone')
def handle_update_zone(data):
    """Update detection zone for a camera"""
    camera_id = data.get('camera_id')
    zone = data.get('zone')
    
    if camera_id and zone:
        camera_zones[camera_id] = zone
        emit('zone_updated', {
            'camera_id': camera_id,
            'zone': zone,
            'message': 'Zone updated successfully'
        })
        print(f'📍 Zone updated for camera {camera_id}: {zone["width"]}x{zone["height"]} at ({zone["x"]}, {zone["y"]})')
    else:
        emit('error', {'message': 'Invalid zone data'})

if __name__ == '__main__':
    print("🚀 Starting SecureEye Human Detection Backend...")
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
    print("👤 Detection Features:")
    print("   - Human detection using Haar cascades")
    print("   - Motion detection")
    print("   - Real-time alerts")
    print("")
    print("🌐 Server starting on http://localhost:5000")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
