# SecureEye Dashboard - Quick Setup Guide

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
1. **Run the startup script:**
   ```bash
   # Windows
   start_dashboard.bat
   
   # Or manually
   python start_server.py
   ```

2. **Open your browser** and go to: `http://localhost:8000/home.html`

### Option 2: Manual Setup

#### Step 1: Start the Backend Server
```bash
cd backend
python app.py
```
The backend will start on `http://localhost:5000`

#### Step 2: Start the Web Server
```bash
# In a new terminal, from the project root
python start_server.py
```
The web server will start on `http://localhost:8000`

#### Step 3: Open the Dashboard
Navigate to: `http://localhost:8000/home.html`

## 🔧 Troubleshooting

### Issue: "Nothing working in the dashboard"

#### 1. Check Backend Connection
- Open `http://localhost:8000/debug.html` in your browser
- Click "Test Backend API" button
- If it fails, make sure the backend is running on port 5000

#### 2. Check Camera Access
- In the debug page, click "Test Camera Access"
- If it fails, check browser permissions:
  - Chrome: Click the camera icon in the address bar
  - Allow camera access for localhost

#### 3. Check WebSocket Connection
- In the debug page, click "Test WebSocket"
- If it fails, restart the backend server

#### 4. Check Firebase Connection
- In the debug page, click "Test Firebase"
- If it fails, check your internet connection

### Common Issues and Solutions

#### Camera Access Denied
**Problem:** Browser blocks camera access
**Solution:** 
1. Click the camera icon in the browser address bar
2. Select "Allow" for camera access
3. Refresh the page

#### Backend Not Starting
**Problem:** Python dependencies missing
**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

#### WebSocket Connection Failed
**Problem:** Backend server not running
**Solution:**
1. Make sure backend is running: `cd backend && python app.py`
2. Check if port 5000 is available
3. Restart the backend server

#### No Cameras Found
**Problem:** No camera devices detected
**Solution:**
1. Connect a camera to your computer
2. Check if camera is working in other applications
3. Try refreshing the page

## 📱 Browser Compatibility

### Supported Browsers:
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Edge 80+
- ✅ Safari 13+

### Required Features:
- Camera API (getUserMedia)
- WebSocket support
- ES6 modules support

## 🔐 Security Notes

- The dashboard runs on localhost for security
- Camera access requires HTTPS in production
- Firebase authentication is used for user management

## 📞 Getting Help

If you're still having issues:

1. **Check the debug page:** `http://localhost:8000/debug.html`
2. **Check browser console:** Press F12 and look for errors
3. **Check backend logs:** Look at the terminal running the backend
4. **Try a different browser:** Some browsers have different camera permissions

## 🎯 Expected Behavior

When everything is working correctly, you should see:

1. **Dashboard loads** with SecureEye branding
2. **Camera feeds appear** in the main area
3. **Activity logs** show successful connections
4. **AI Detection buttons** are available on each camera
5. **WebSocket connection** shows as connected in logs

## 🔄 Restart Everything

If you need to restart everything:

1. **Stop all servers** (Ctrl+C in terminals)
2. **Wait 5 seconds**
3. **Run the startup script again:**
   ```bash
   start_dashboard.bat
   ```

---

**Need more help?** Check the browser console (F12) for detailed error messages.
