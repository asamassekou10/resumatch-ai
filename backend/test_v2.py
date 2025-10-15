#!/usr/bin/env python3
"""
Quick test script for ResumeAnalyzer AI v2.0
This script tests the basic functionality without requiring a full setup
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all new modules can be imported"""
    print("🔄 Testing imports...")
    
    try:
        # Test configuration
        from config import get_config, DevelopmentConfig
        print("✅ Config module imported")
        
        # Test models
        from models import db, User, Analysis
        print("✅ Models imported")
        
        # Test error handling
        from errors import APIError, ValidationError, register_error_handlers
        print("✅ Error handling imported")
        
        # Test validators
        from validators import FileValidator, TextValidator
        print("✅ Validators imported")
        
        # Test AI processor (without spaCy model)
        from ai_processor import AIProcessor
        print("✅ AI processor imported")
        
        # Test Gemini service
        from gemini_service import GeminiService
        print("✅ Gemini service imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    print("\n🔄 Testing configuration...")
    
    try:
        from config import get_config, DevelopmentConfig
        
        # Test default config
        config = get_config()
        print(f"✅ Default config: {config.__name__}")
        
        # Test environment-specific config
        os.environ['FLASK_ENV'] = 'development'
        config = get_config()
        print(f"✅ Development config: {config.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_ai_processor():
    """Test AI processor initialization"""
    print("\n🔄 Testing AI processor...")
    
    try:
        from ai_processor import AIProcessor
        
        # Initialize processor (this will work even without spaCy model)
        processor = AIProcessor()
        print("✅ AI processor initialized")
        
        # Test text preprocessing
        test_text = "Python developer with Flask experience"
        processed = processor._preprocess_text(test_text)
        print(f"✅ Text preprocessing works: '{processed}'")
        
        return True
        
    except Exception as e:
        print(f"❌ AI processor test failed: {e}")
        return False

def test_gemini_service():
    """Test Gemini service initialization"""
    print("\n🔄 Testing Gemini service...")
    
    try:
        from gemini_service import GeminiService
        
        # Initialize service
        service = GeminiService()
        print("✅ Gemini service initialized")
        
        # Test fallback feedback generation
        feedback = service._generate_fallback_feedback(75.5, ['python', 'flask'])
        print(f"✅ Fallback feedback works: {feedback[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")
        return False

def test_validators():
    """Test validation functions"""
    print("\n🔄 Testing validators...")
    
    try:
        from validators import TextValidator, FileValidator
        
        # Test email validation
        valid_email = TextValidator.validate_email("test@example.com")
        print(f"✅ Email validation works: {valid_email}")
        
        # Test password validation
        try:
            TextValidator.validate_password("weak")
            print("❌ Password validation should have failed")
            return False
        except Exception:
            print("✅ Password validation correctly rejects weak passwords")
        
        return True
        
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\n🔄 Testing Flask app creation...")
    
    try:
        # Set test environment
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['SECRET_KEY'] = 'test-secret'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
        
        from app import create_app
        
        # Create app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            print(f"✅ Health endpoint works: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ResumeAnalyzer AI v2.0 Quick Test")
    print("=" * 40)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    tests = [
        test_imports,
        test_configuration,
        test_ai_processor,
        test_gemini_service,
        test_validators,
        test_app_creation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new version is ready to use.")
        print("\nNext steps:")
        print("1. Set up your .env file with real values")
        print("2. Run: python test_setup.py")
        print("3. Or start the server directly: python app.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
