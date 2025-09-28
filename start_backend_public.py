#!/usr/bin/env python3
"""
Quick start script for exposing backend publicly with ngrok.
Run this to make your local backend accessible to CloudFront.
"""

import os
import sys
import time
import subprocess
from pyngrok import ngrok

def main():
    print("🚀 AIHRI Backend - Public Access Setup")
    print("=" * 50)
    
    # Check if ngrok auth token is set
    auth_token = os.getenv('NGROK_AUTH_TOKEN')
    if not auth_token:
        print("❌ NGROK_AUTH_TOKEN not found!")
        print("\nTo get your token:")
        print("1. Go to https://ngrok.com/")
        print("2. Sign up for a free account")
        print("3. Get your auth token from https://dashboard.ngrok.com/get-started/yourauthtoken")
        print("4. Set it as an environment variable:")
        print("   Windows: $env:NGROK_AUTH_TOKEN='your_token_here'")
        print("   Linux/Mac: export NGROK_AUTH_TOKEN='your_token_here'")
        return
    
    # Set ngrok auth token
    ngrok.set_auth_token(auth_token)
    
    print("✅ ngrok auth token found")
    print("📡 Starting Django server...")
    
    # Start Django server
    try:
        django_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for Django to start
        time.sleep(5)
        
        # Create ngrok tunnel
        print("🌐 Creating public tunnel...")
        tunnel = ngrok.connect(8000, "http")
        
        public_url = tunnel.public_url
        api_url = f"{public_url}/api"
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Your backend is now public")
        print("=" * 50)
        print(f"🌍 Public URL: {public_url}")
        print(f"🔗 API Endpoint: {api_url}")
        print(f"📊 API Docs: {public_url}/api/schema/swagger-ui/")
        print("\n📝 Next steps:")
        print(f"1. Update your frontend's .env.local file:")
        print(f"   NEXT_PUBLIC_API_URL={api_url}")
        print("2. Build and deploy your frontend to CloudFront")
        print("3. Test the connection")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        try:
            ngrok.disconnect(tunnel.public_url)
            ngrok.kill()
            django_process.terminate()
        except:
            pass
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()



