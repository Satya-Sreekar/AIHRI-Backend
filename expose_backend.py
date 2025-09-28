#!/usr/bin/env python3
"""
Script to expose local Django backend to the internet using ngrok.
This allows your CloudFront-hosted frontend to communicate with your local backend.
"""

import os
import sys
import time
from pyngrok import ngrok, conf
from django.core.management import execute_from_command_line

def main():
    print("🚀 Starting Django backend with ngrok tunnel...")
    
    # Get ngrok auth token from environment or prompt user
    auth_token = os.getenv('NGROK_AUTH_TOKEN')
    if not auth_token:
        print("\n⚠️  NGROK_AUTH_TOKEN not found in environment variables.")
        print("Please get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken")
        auth_token = input("Enter your ngrok auth token: ").strip()
        if not auth_token:
            print("❌ No auth token provided. Exiting.")
            return
    
    # Set ngrok auth token
    ngrok.set_auth_token(auth_token)
    
    # Start Django server
    print("\n📡 Starting Django server on port 8000...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ollama_api.settings')
    
    # Start Django in a separate process
    import subprocess
    django_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
    ])
    
    # Wait a moment for Django to start
    time.sleep(3)
    
    try:
        # Create ngrok tunnel
        print("🌐 Creating ngrok tunnel...")
        tunnel = ngrok.connect(8000, "http")
        
        public_url = tunnel.public_url
        print(f"\n✅ Backend is now accessible at: {public_url}")
        print(f"🔗 API endpoint: {public_url}/api/")
        print(f"📊 API docs: {public_url}/api/schema/swagger-ui/")
        print(f"\n📝 Update your frontend's NEXT_PUBLIC_API_URL to: {public_url}/api")
        print("\n⏹️  Press Ctrl+C to stop the server and tunnel")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"❌ Error creating ngrok tunnel: {e}")
    finally:
        # Clean up
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()
        django_process.terminate()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()



