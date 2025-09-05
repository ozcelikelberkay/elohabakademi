#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EHM Akademi - Ngrok Live Deployment Launcher
This script launches your Flask application with ngrok for live access
"""

import subprocess
import sys
import os

def check_and_install_requirements():
    """Check and install required packages"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'flask',
        'flask-sqlalchemy', 
        'werkzeug',
        'pyngrok'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} - Installed")

def main():
    """Main launcher function"""
    print("🚀 EHM Akademi - Ngrok Live Deployment")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please run this script from the project directory.")
        input("Press Enter to exit...")
        return
    
    # Check and install requirements
    check_and_install_requirements()
    
    print("\n🌐 Starting live deployment with ngrok...")
    print("⚠️  Important Notes:")
    print("   • Keep this window open to maintain the connection")
    print("   • The ngrok URL will change each time you restart")
    print("   • Share the ngrok URL with others to access your app")
    print("   • Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    # Launch the Flask app with ngrok
    try:
        import app
        print("🎯 Application started successfully!")
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()