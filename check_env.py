import os
import sys
import platform

def check_environment():
    """Check if the environment is properly set up for running SmartReminder."""
    print("Environment Check for SmartReminder")
    print("-" * 40)
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python Version: {python_version}")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    else:
        print("✅ Python version OK")
    
    # Check data directory
    if os.path.exists('data'):
        print("✅ Data directory exists")
    else:
        print("ℹ️ Data directory will be created automatically on first run")
    
    # Check for venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Running in a virtual environment")
    else:
        print("⚠️ Not running in a virtual environment. It's recommended to use a virtual environment.")
    
    # Check required packages
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask is not installed. Run: pip install -r requirements.txt")
        return False
    
    print("-" * 40)
    print("Environment check complete")
    return True

if __name__ == "__main__":
    success = check_environment()
    if not success:
        print("\nPlease fix the issues above before running the application.")
        sys.exit(1)
    else:
        print("\nEnvironment looks good! You can run the application with: python run.py")