#!/usr/bin/env python3
"""
Test setup script for ResumeAnalyzer AI v2.0
Run this script to set up and test the new version
"""

import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file for testing"""
    env_content = """# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_optimizer
DEV_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_optimizer_dev
TEST_DATABASE_URL=sqlite:///:memory:

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production

# AI Services
GEMINI_API_KEY=your-gemini-api-key-here

# Environment
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Optional: Redis for caching (leave empty if not using Redis)
REDIS_URL=
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def download_spacy_model():
    """Download spaCy model"""
    print("🧠 Downloading spaCy model...")
    try:
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
        print("✅ spaCy model downloaded")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        return False
    return True

def setup_database():
    """Set up database"""
    print("🗄️  Setting up database...")
    try:
        # Import and test database connection
        from models import db
        from app import create_app
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    try:
        subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], check=True)
        print("✅ All tests passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False
    return True

def start_server():
    """Start the development server"""
    print("🚀 Starting development server...")
    print("📱 The server will be available at: http://localhost:5000")
    print("📊 API endpoints will be at: http://localhost:5000/api/v1")
    print("🏥 Health check: http://localhost:5000/api/v1/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

def main():
    """Main test setup function"""
    print("🔧 ResumeAnalyzer AI v2.0 Test Setup")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Setup steps
    steps = [
        ("Creating environment file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Downloading spaCy model", download_spacy_model),
        ("Setting up database", setup_database),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    
    # Ask user what they want to do next
    print("\nWhat would you like to do next?")
    print("1. Run tests")
    print("2. Start development server")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        run_tests()
    elif choice == "2":
        start_server()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
