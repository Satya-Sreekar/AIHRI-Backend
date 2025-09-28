#!/usr/bin/env python3
"""
Setup script for Django Ollama API
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create a virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def activate_virtual_environment():
    """Activate virtual environment based on OS"""
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"
    
    if os.path.exists(activate_script):
        print("✅ Virtual environment activation script found")
        return True
    else:
        print("❌ Virtual environment activation script not found")
        return False

def install_dependencies():
    """Install Python dependencies"""
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")

def run_migrations():
    """Run Django migrations"""
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    return run_command(f"{python_cmd} manage.py migrate", "Running Django migrations")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    env_content = """# Django Ollama API Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Django Settings (optional)
# DEBUG=True
# SECRET_KEY=your-secret-key-here
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Django Ollama API")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Check virtual environment activation
    if not activate_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure Ollama is installed and running")
    print("2. Start the Django server: python manage.py runserver")
    print("3. Access the API at: http://localhost:8000/api/")
    print("4. View documentation at: http://localhost:8000/api/docs/")
    print("5. Test the API with: python test_api.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 