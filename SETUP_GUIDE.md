# SecureEye Setup Guide

This guide will help you set up and run the SecureEye surveillance system.

## Prerequisites

### Required Software
- **Python 3.8+** - Download from [python.org](https://python.org)
- **Node.js 16+** (optional, for additional tools) - Download from [nodejs.org](https://nodejs.org)
- **Modern Web Browser** - Chrome, Firefox, Edge, or Safari
- **Camera Device** - USB webcam or IP camera

### Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: `eye-61167`
3. Enable Authentication, Firestore, and Cloud Messaging

## Backend Setup

### 1. Install Python Dependencies

**Windows:**
```bash
cd backend
setup.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 2. Configure Firebase Service Account

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Replace `backend/firebase-service-account.json` with your downloaded file
5. Update `backend/.env` with your Firebase credentials

### 3. Run the Backend

```bash
cd backend
# Activate virtual environment
venv\Scripts\activate.bat  # Windows
source venv/bin/activate   # Linux/Mac

# Run the server
python app.py
```

The backend will start on `http://localhost:5000`

## Frontend Setup

### 1. Serve the Frontend

You can serve the frontend in several ways:

**Option 1: Python HTTP Server**
```bash
# From the project root
python -m http.server 8000
```

**Option 2: Node.js HTTP Server**
```bash
# Install http-server globally
npm install -g http-server

# Serve the files
http-server -p 8000
```

**Option 3: Live Server (VS Code Extension)**
- Install "Live Server" extension in VS Code
- Right-click on `landing.html` and select "Open with Live Server"

### 2. Access the Application

Open your browser and go to `http://localhost:8000`

## Configuration

### Firebase Configuration

The Firebase configuration is already set up in `firebase-config.js`:
- Project ID: `eye-61167`
- Authentication, Firestore, and Messaging are enabled

### Camera Setup

1. **USB Cameras**: Connect your USB webcam to your computer
2. **IP Cameras**: Configure your IP camera and note the stream URL
3. **Permissions**: Allow camera access when prompted by the browser

### Notification Setup

1. **Push Notifications**: The app will request notification permission
2. **Email Notifications**: Configure SMTP settings in the backend (optional)
3. **SMS Notifications**: Configure Twilio or similar service (optional)

## Usage

### 1. Authentication
- **Sign Up**: Create a new account with email and password
- **Sign In**: Use your credentials to log in
- **Google Sign-In**: Available on the landing page

### 2. Dashboard
- **Camera Feeds**: View live camera feeds
- **AI Detection**: Start AI-powered surveillance
- **Activity Logs**: Monitor detection events
- **Settings**: Configure detection sensitivity and notifications

### 3. AI Detection Features
- **Fire Detection**: Color-based fire detection
- **Motion Detection**: Background subtraction motion detection
- **Violence Detection**: Rapid motion analysis
- **Crowd Detection**: Edge density analysis

## API Endpoints

The backend provides the following endpoints:

- `GET /api/health` - Health check
- `GET /api/cameras` - List active cameras
- `POST /api/cameras` - Add a new camera
- `DELETE /api/cameras/<id>` - Remove a camera

### WebSocket Events

- `start_detection` - Start AI detection for a camera
- `stop_detection` - Stop AI detection for a camera
- `detection_alert` - Receive detection alerts

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check camera permissions in browser settings
   - Ensure camera is not being used by another application
   - Try refreshing the page

2. **Backend Connection Failed**
   - Ensure backend is running on port 5000
   - Check firewall settings
   - Verify WebSocket connection

3. **Firebase Authentication Issues**
   - Check Firebase project configuration
   - Verify service account credentials
   - Ensure Authentication is enabled in Firebase Console

4. **AI Detection Not Working**
   - Check camera feed quality
   - Adjust detection sensitivity in settings
   - Ensure good lighting conditions

### Debug Mode

Enable debug mode by setting `DEBUG=True` in `backend/.env`:
- Detailed logging in console
- Error stack traces
- WebSocket connection status

## Security Considerations

1. **Firebase Security Rules**: Configure Firestore security rules
2. **HTTPS**: Use HTTPS in production
3. **API Keys**: Keep service account keys secure
4. **Camera Access**: Monitor camera permissions

## Production Deployment

### Backend Deployment

1. **Environment Variables**: Set production environment variables
2. **SSL Certificate**: Configure HTTPS
3. **Process Manager**: Use PM2 or similar for process management
4. **Reverse Proxy**: Use Nginx or Apache

### Frontend Deployment

1. **Static Hosting**: Deploy to Firebase Hosting, Netlify, or similar
2. **CDN**: Use a CDN for better performance
3. **HTTPS**: Ensure SSL certificate is configured

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Firebase documentation
3. Check browser console for errors
4. Verify network connectivity

## Features

### Current Features
- ✅ User Authentication (Email/Password, Google)
- ✅ Real-time Camera Feeds
- ✅ AI-powered Detection (Fire, Motion, Violence, Crowd)
- ✅ WebSocket Communication
- ✅ Activity Logging
- ✅ Push Notifications
- ✅ Responsive UI
- ✅ Settings Management

### Planned Features
- 🔄 Email/SMS Notifications
- 🔄 Advanced AI Models
- 🔄 Mobile App
- 🔄 Multi-user Support
- 🔄 Cloud Storage
- 🔄 Analytics Dashboard

## License

This project is for educational and demonstration purposes.
