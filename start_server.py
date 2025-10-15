#!/usr/bin/env python3
"""
Simple HTTP server for SecureEye Dashboard
This serves the dashboard files over HTTP, which is required for camera access
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import time
import threading
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def start_server(port=8000):
    """Start the HTTP server"""
    try:
        # Change to the project directory
        project_dir = Path(__file__).parent
        os.chdir(project_dir)
        
        # Create server
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 SecureEye Dashboard Server starting on port {port}")
            print(f"📁 Serving files from: {project_dir}")
            print(f"🌐 Dashboard URL: http://localhost:{port}/home.html")
            print(f"🔧 Debug URL: http://localhost:{port}/debug.html")
            print("=" * 60)
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open(f'http://localhost:{port}/home.html')
                except:
                    pass
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 8000.")
    
    start_server(port)
