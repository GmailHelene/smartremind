import os
import sys
import platform
import subprocess
from dotenv import load_dotenv

def check_environment():
    """Check if the environment is properly set up for running SmartReminder."""
    print("Environment Check for SmartReminder")
    print("-" * 40)
    
    # Check Python version
    python_version = platform.python_version()
    print(f"Python version: {python_version}")
    
    # Check if required directories exist
    required_dirs = ['data', 'templates', 'static']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ Directory '{directory}' exists")
        else:
            print(f"✗ Directory '{directory}' is missing")
            os.makedirs(directory, exist_ok=True)
            print(f"  - Created '{directory}' directory")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✓ .env file exists")
        load_dotenv()
    else:
        print("✗ .env file is missing")
        print("  - Creating default .env file")
        with open('.env', 'w') as f:
            f.write("# SmartReminder Environment Variables\n")
            f.write("SECRET_KEY=dev-key-for-smartreminder\n")
            f.write("MAIL_SERVER=smtp.gmail.com\n")
            f.write("MAIL_PORT=587\n")
            f.write("MAIL_USE_TLS=true\n")
            f.write("MAIL_USERNAME=\n")
            f.write("MAIL_PASSWORD=\n")
            f.write("MAIL_DEFAULT_SENDER=\n")
        print("  - Default .env file created. Please update it with your settings.")
    
    # Check if database exists
    if os.path.exists('smartreminder.db'):
        print("✓ Database file exists")
    else:
        print("✗ Database file is missing")
        print("  - Database will be created on first run")
    
    # Check requirements
    try:
        import flask
        print("✓ Flask is installed")
    except ImportError:
        print("✗ Flask is not installed")
        print("  - Please run: pip install -r requirements.txt")
    
    print("\nEnvironment check completed.")
    print("-" * 40)
    return True

def run_app():
    """Run the SmartReminder application."""
    from app import app
    
    # Check if port is specified
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', '1', 't']
    
    print(f"\nStarting SmartReminder on port {port} (debug={debug})")
    print("Press CTRL+C to quit\n")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    check_environment()
    
    # Run the app if environment check passed
    print("\nPress Enter to start the application or CTRL+C to cancel...")
    try:
        input()
        run_app()
    except KeyboardInterrupt:
        print("\nApplication startup cancelled.")
        sys.exit(0)