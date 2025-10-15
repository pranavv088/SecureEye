# SecureEye Production Configuration

## Environment Variables
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
DEBUG=False

## Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
FRONTEND_PORT=8000

## Firebase Configuration (Optional)
# Add your Firebase service account file as:
# backend/firebase-service-account.json

## Features Enabled
ZONE_DETECTION=true
MOTION_DETECTION=true
BEEP_ALERTS=true
WEBSOCKET_COMMUNICATION=true

## Production Notes
- Debug mode is disabled
- Firebase is optional
- Only essential features are enabled
- Clean startup without verbose logging
