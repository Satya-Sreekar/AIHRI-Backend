#!/usr/bin/env python3
"""
Simple script to start Django server on 0.0.0.0:8000
This makes the backend accessible from all network interfaces.
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting AIHRI Backend on 0.0.0.0:8000")
    print("=" * 50)
    print("📡 Backend will be accessible at:")
    print("   - Local:  http://localhost:8000")
    print("   - Network: http://0.0.0.0:8000")
    print("   - API:    http://0.0.0.0:8000/api/")
    print("   - Docs:   http://0.0.0.0:8000/api/docs/")
    print("=" * 50)
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    try:
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ollama_api.settings')
        
        # Start Django server on all interfaces
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
