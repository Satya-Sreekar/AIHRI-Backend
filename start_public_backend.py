#!/usr/bin/env python3
"""
Start Django backend to accept requests from all IPs.
Perfect for when you have a static public IP.
"""

import os
import sys
import subprocess
import socket

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "localhost"

def get_public_ip():
    """Try to get the public IP address."""
    try:
        import requests
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except Exception:
        return "unknown"

def main():
    print("🚀 AIHRI Backend - Public IP Setup")
    print("=" * 50)
    
    # Get IP addresses
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"🏠 Local IP: {local_ip}")
    print(f"🌍 Public IP: {public_ip}")
    print(f"🔌 Port: 8000")
    print()
    
    # Show connection URLs
    print("📡 Your backend will be accessible at:")
    print(f"   Local:  http://{local_ip}:8000")
    print(f"   Public: http://{public_ip}:8000")
    print(f"   API:    http://{public_ip}:8000/api/")
    print()
    
    # Check if port is available
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 8000))
            s.listen(1)
            s.close()
    except OSError:
        print("❌ Port 8000 is already in use!")
        print("   Please stop any other Django server or change the port.")
        return
    
    print("✅ Port 8000 is available")
    print()
    
    # Start Django server
    print("🚀 Starting Django server on all interfaces...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ollama_api.settings')
        
        # Start Django server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()



