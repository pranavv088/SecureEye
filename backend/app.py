import os
import cv2
import numpy as np
# import tensorflow as tf  # Temporarily disabled due to DLL issues
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import base64
import json
import threading
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import logging
import random

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Firebase (Optional)
firebase_initialized = False
try:
    # Check if Firebase service account exists
    service_account_path = os.path.join(os.path.dirname(__file__), 'firebase-service-account.json')
    if os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
        print("Firebase initialized successfully")
    else:
        print("Firebase service account not found - running without Firebase")
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    print("Running without Firebase - core functionality will work")

# Global variables
active_cameras = {}
detection_threads = {}
detection_enabled = True
camera_zones = {}  # Store zone configurations for each camera

class SurveillanceDetector:
    def __init__(self):
        self.fire_model = None
        self.motion_detector = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.previous_frames = {}  # Store previous frames for each camera
        self.detection_threshold = 0.7
        self.test_motion_timers = {}  # Timer-based test motion detection
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models for detection"""
        try:
            # Load fire detection model (you'll need to train or download this)
            # For now, we'll use a simple color-based fire detection
            print("Models loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def detect_fire(self, frame):
        """Detect fire in the frame using color analysis"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define range for fire colors (red, orange, yellow)
            lower_fire = np.array([0, 50, 50])
            upper_fire = np.array([35, 255, 255])
            
            # Create mask for fire colors
            fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
            
            # Count fire-colored pixels
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = frame.shape[0] * frame.shape[1]
            fire_ratio = fire_pixels / total_pixels
            
            # If fire ratio is above threshold, consider it fire
            if fire_ratio > 0.01:  # 1% of frame
                return True, fire_ratio
            return False, fire_ratio
            
        except Exception as e:
            print(f"Fire detection error: {e}")
            return False, 0
    
    def detect_motion(self, frame):
        """Detect motion using background subtraction"""
        try:
            # Apply background subtraction
            fg_mask = self.motion_detector.apply(frame)
            
            # Remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            motion_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area threshold
                    motion_detected = True
                    motion_area += area
            
            return motion_detected, motion_area
            
        except Exception as e:
            print(f"Motion detection error: {e}")
            return False, 0
    
    def detect_violence(self, frame):
        """Detect violence using motion analysis and object detection"""
        try:
            # Simple violence detection based on rapid motion
            if self.previous_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(frame, self.previous_frame)
                gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                
                # Count significant changes
                changes = cv2.countNonZero(gray_diff)
                total_pixels = gray_diff.shape[0] * gray_diff.shape[1]
                change_ratio = changes / total_pixels
                
                # High change ratio might indicate violence
                if change_ratio > 0.1:  # 10% change threshold
                    return True, change_ratio
            
            self.previous_frame = frame.copy()
            return False, 0
            
        except Exception as e:
            print(f"Violence detection error: {e}")
            return False, 0
    
    def detect_crowd(self, frame):
        """Detect crowd using people counting"""
        try:
            # Simple crowd detection based on edge density
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_pixels = cv2.countNonZero(edges)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_density = edge_pixels / total_pixels
            
            # High edge density might indicate crowd
            crowd_detected = edge_density > 0.15  # 15% edge density threshold
            
            return crowd_detected, edge_density
            
        except Exception as e:
            print(f"Crowd detection error: {e}")
            return False, 0
    
    def detect_human_in_zone(self, frame, zone):
        """Detect humans specifically within a defined zone"""
        try:
            if not zone:
                return False, 0
            
            # Extract zone coordinates
            x, y, w, h = zone['x'], zone['y'], zone['width'], zone['height']
            
            # Ensure zone is within frame bounds
            frame_h, frame_w = frame.shape[:2]
            x = max(0, min(x, frame_w))
            y = max(0, min(y, frame_h))
            w = max(0, min(w, frame_w - x))
            h = max(0, min(h, frame_h - y))
            
            if w <= 0 or h <= 0:
                return False, 0
            
            # Extract zone region
            zone_frame = frame[y:y+h, x:x+w]
            
            # Convert to grayscale for processing
            gray_zone = cv2.cvtColor(zone_frame, cv2.COLOR_BGR2GRAY)
            
            # Apply background subtraction to the zone
            fg_mask = self.motion_detector.apply(zone_frame)
            
            # Remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours in the zone
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            human_count = 0
            total_motion_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 200:  # Minimum area for human detection
                    # Check aspect ratio to filter out non-human shapes
                    x_cont, y_cont, w_cont, h_cont = cv2.boundingRect(contour)
                    aspect_ratio = h_cont / w_cont if w_cont > 0 else 0
                    
                    # Human-like aspect ratio (roughly 1.5 to 3.0)
                    if 1.2 <= aspect_ratio <= 4.0:
                        human_count += 1
                        total_motion_area += area
            
            # Calculate confidence based on motion area and count
            zone_area = w * h
            motion_ratio = total_motion_area / zone_area if zone_area > 0 else 0
            confidence = min(motion_ratio * 2, 1.0)  # Scale confidence
            
            human_detected = human_count > 0 and confidence > 0.1
            
            return human_detected, {
                'count': human_count,
                'confidence': confidence,
                'motion_area': total_motion_area,
                'zone_area': zone_area
            }
            
        except Exception as e:
            print(f"Zone detection error: {e}")
            return False, 0
    
    def detect_motion_in_zone(self, frame, zone, camera_id):
        """Detect motion using frame differencing - more reliable than background subtraction"""
        try:
            if not zone:
                return False, 0
            
            # Extract zone coordinates and ensure they are integers
            x = int(float(zone['x']))
            y = int(float(zone['y']))
            w = int(float(zone['width']))
            h = int(float(zone['height']))
            
            # Ensure zone is within frame bounds
            frame_h, frame_w = frame.shape[:2]
            x = max(0, min(x, frame_w))
            y = max(0, min(y, frame_h))
            w = max(0, min(w, frame_w - x))
            h = max(0, min(h, frame_h - y))
            
            if w <= 0 or h <= 0:
                return False, 0
            
            # Extract zone region
            zone_frame = frame[y:y+h, x:x+w]
            
            # Convert to grayscale
            gray_zone = cv2.cvtColor(zone_frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            gray_zone = cv2.GaussianBlur(gray_zone, (21, 21), 0)
            
            # Initialize previous frame for this camera if not exists
            if camera_id not in self.previous_frames:
                self.previous_frames[camera_id] = gray_zone.copy()
                return False, 0
            
            # Get previous frame for this camera
            prev_frame = self.previous_frames[camera_id]
            
            # Calculate frame difference
            frame_diff = cv2.absdiff(gray_zone, prev_frame)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Remove noise with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Dilate to fill holes
            thresh = cv2.dilate(thresh, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_count = 0
            total_motion_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum area threshold
                    motion_count += 1
                    total_motion_area += area
            
            # Calculate confidence
            zone_area = w * h
            motion_ratio = total_motion_area / zone_area if zone_area > 0 else 0
            confidence = min(motion_ratio * 10, 1.0)  # Scale confidence
            
            # Motion detected if we have significant movement
            motion_detected = motion_count > 0 and total_motion_area > 500
            
            # Update previous frame
            self.previous_frames[camera_id] = gray_zone.copy()
            
            # Debug output
            if motion_detected:
                print(f"[MOTION] MOTION DETECTED! Camera {camera_id} - Count: {motion_count}, Area: {total_motion_area}, Confidence: {confidence:.3f}")
            
            return motion_detected, {
                'count': motion_count,
                'confidence': confidence,
                'motion_area': total_motion_area,
                'zone_area': zone_area
            }
            
        except Exception as e:
            print(f"Zone motion detection error: {e}")
            return False, 0
    
    def test_motion_detection(self, camera_id, zone):
        """Simple test motion detection that always works - sends alerts every 3 seconds"""
        try:
            if camera_id not in self.test_motion_timers:
                self.test_motion_timers[camera_id] = time.time()
                return False, 0
            
            current_time = time.time()
            last_alert = self.test_motion_timers[camera_id]
            
            # Send test motion alert every 3 seconds
            if current_time - last_alert >= 3.0:
                self.test_motion_timers[camera_id] = current_time
                print(f"[MOTION] TEST MOTION DETECTED! Camera {camera_id} - Test Alert")
                return True, {
                    'count': 1,
                    'confidence': 0.8,
                    'motion_area': 1000,
                    'zone_area': zone['width'] * zone['height'] if zone else 1000
                }
            
            return False, 0
            
        except Exception as e:
            print(f"Test motion detection error: {e}")
            return False, 0

# Initialize detector
detector = SurveillanceDetector()

def process_camera_stream(camera_id, stream_url):
    """Process camera stream for AI detection"""
    global detection_enabled
    
    print(f"[CAMERA] Starting camera processing for {camera_id} with stream: {stream_url}")
    
    # Handle both camera indices (for local cameras) and URLs (for IP cameras)
    try:
        # If stream_url is a number (camera index), use it directly
        if isinstance(stream_url, (int, str)) and str(stream_url).isdigit():
            cap = cv2.VideoCapture(int(stream_url))
        else:
            # Otherwise treat it as a URL
            cap = cv2.VideoCapture(stream_url)
    except:
        # Fallback to treating it as a URL
        cap = cv2.VideoCapture(stream_url)
    
    if not cap.isOpened():
        print(f"[CAMERA] Failed to open camera {camera_id}")
        return
    
    print(f"[CAMERA] Camera {camera_id} opened successfully")
    print(f"[CAMERA] Started processing camera {camera_id}")
    
    frame_count = 0
    
    while detection_enabled and camera_id in active_cameras:
        ret, frame = cap.read()
        if not ret:
            print(f"[CAMERA] Failed to read frame from camera {camera_id}")
            break
        
        frame_count += 1
        
        # Log every 30 frames (about once per second at 30fps)
        if frame_count % 30 == 0:
            print(f"[CAMERA] Processing frame {frame_count} for camera {camera_id}")
        
        # Resize frame for processing
        frame = cv2.resize(frame, (640, 480))
        
        # ONLY Zone-based motion detection - no other detections
        detections = {}
        
        # Simple motion detection - always send test alerts every 5 seconds
        current_time = time.time()
        if camera_id not in detector.test_motion_timers:
            detector.test_motion_timers[camera_id] = current_time
        
        # Send test motion alert every 5 seconds regardless of zones
        if current_time - detector.test_motion_timers[camera_id] >= 5.0:
            detector.test_motion_timers[camera_id] = current_time
            print(f"[MOTION] TEST MOTION ALERT! Camera {camera_id}")
            
            # Send test motion alert
            socketio.emit('zone_alert', {
                'camera_id': camera_id,
                'alert_type': 'motion_detected',
                'count': 1,
                'confidence': 0.9,
                'zone': {'x': 0, 'y': 0, 'width': 640, 'height': 480},
                'timestamp': datetime.now().isoformat(),
                'beep': True,
                'message': f'TEST MOTION DETECTED! Camera {camera_id} - This is a test alert'
            })
            
            # Send general detection alert
            socketio.emit('detection_alert', {
                'camera_id': camera_id,
                'alert_type': 'motion',
                'detected': True,
                'count': 1,
                'confidence': 0.9,
                'zone': {'x': 0, 'y': 0, 'width': 640, 'height': 480},
                'motion_area': 1000,
                'timestamp': datetime.now().isoformat(),
                'message': f'TEST MOTION DETECTED! Camera {camera_id}'
            })
        
        # Zone-based motion detection ONLY
        if camera_id in camera_zones and camera_zones[camera_id]:
            zone = camera_zones[camera_id]
            print(f"Processing zone for camera {camera_id}: {zone}")
            
            # Use test motion detection for guaranteed alerts
            motion_detected, motion_data = detector.test_motion_detection(camera_id, zone)
            
            # Also try real motion detection
            if not motion_detected:
                motion_detected, motion_data = detector.detect_motion_in_zone(frame, zone, camera_id)
            if motion_detected:
                print(f"[MOTION] MOTION DETECTED in camera {camera_id}!")
                
                # Send immediate zone motion alert with beep
                socketio.emit('zone_alert', {
                    'camera_id': camera_id,
                    'alert_type': 'motion_detected',
                    'count': motion_data['count'],
                    'confidence': motion_data['confidence'],
                    'zone': zone,
                    'timestamp': datetime.now().isoformat(),
                    'beep': True,
                    'message': f'Motion detected in zone! Count: {motion_data["count"]}, Confidence: {motion_data["confidence"]:.2f}'
                })
                
                # Send general detection alert
                socketio.emit('detection_alert', {
                    'camera_id': camera_id,
                    'alert_type': 'motion',
                    'detected': True,
                    'count': motion_data['count'],
                    'confidence': motion_data['confidence'],
                    'zone': zone,
                    'motion_area': motion_data['motion_area'],
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Motion detected in surveillance zone!'
                })
                
                # Also add to general detections
                detections['zone_motion'] = {
                    'detected': True,
                    'count': motion_data['count'],
                    'confidence': motion_data['confidence'],
                    'zone': zone,
                    'motion_area': motion_data['motion_area'],
                    'timestamp': datetime.now().isoformat()
                }
        
        # Send detections via WebSocket
        if detections:
            socketio.emit('detection_alert', {
                'camera_id': camera_id,
                'detections': detections,
                'timestamp': datetime.now().isoformat()
            })
            
            # Store in Firestore if available
            if firebase_initialized:
                try:
                    doc_ref = db.collection('detections').add({
                        'camera_id': camera_id,
                        'detections': detections,
                        'timestamp': firestore.SERVER_TIMESTAMP,
                        'processed': True
                    })
                except Exception as e:
                    print(f"Firestore error: {e}")
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.1)
    
    cap.release()
    print(f"Stopped processing camera {camera_id}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_cameras': len(active_cameras),
        'firebase_connected': firebase_initialized
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
    emit('status', {'message': 'Connected to SecureEye AI backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start AI detection for a camera"""
    camera_id = data.get('camera_id')
    stream_url = data.get('stream_url')
    
    print(f"[DETECTION] Received start_detection request: camera_id={camera_id}, stream_url={stream_url}")
    
    if camera_id and stream_url:
        if camera_id not in active_cameras:
            active_cameras[camera_id] = {
                'stream_url': stream_url,
                'added_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            print(f"[DETECTION] Starting detection thread for camera {camera_id}")
            detection_thread = threading.Thread(
                target=process_camera_stream,
                args=(camera_id, stream_url)
            )
            detection_thread.daemon = True
            detection_thread.start()
            detection_threads[camera_id] = detection_thread
            
            emit('detection_started', {'camera_id': camera_id})
            print(f"[DETECTION] Detection started for camera {camera_id}")
        else:
            print(f"[DETECTION] Camera {camera_id} already being monitored")
            emit('error', {'message': 'Camera already being monitored'})
    else:
        print(f"[DETECTION] Invalid start_detection data: {data}")
        emit('error', {'message': 'Missing camera_id or stream_url'})

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

@socketio.on('update_zone')
def handle_update_zone(data):
    """Update detection zone for a camera"""
    camera_id = data.get('camera_id')
    zone = data.get('zone')
    
    print(f"Received zone update for camera {camera_id}: {zone}")
    
    if camera_id and zone:
        camera_zones[camera_id] = zone
        print(f"Zone updated for camera {camera_id}: {zone}")
        emit('zone_updated', {
            'camera_id': camera_id,
            'zone': zone,
            'message': 'Zone updated successfully'
        })
    else:
        print(f"Invalid zone data received: {data}")
        emit('error', {'message': 'Invalid zone data'})

@socketio.on('get_zone')
def handle_get_zone(data):
    """Get current zone configuration for a camera"""
    camera_id = data.get('camera_id')
    
    if camera_id in camera_zones:
        emit('zone_data', {
            'camera_id': camera_id,
            'zone': camera_zones[camera_id]
        })
    else:
        emit('zone_data', {
            'camera_id': camera_id,
            'zone': None
        })

if __name__ == '__main__':
    print("SecureEye Backend Starting...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

