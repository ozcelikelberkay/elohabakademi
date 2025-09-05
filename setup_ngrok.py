#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EHM Akademi - Ngrok Setup Helper
This script helps you configure ngrok authentication
"""

import subprocess
import sys
import os

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    print("🔧 Ngrok Authentication Setup")
    print("=" * 40)
    print()
    
    print("📋 Steps to get your auth token:")
    print("1. Go to: https://dashboard.ngrok.com/signup")
    print("2. Create a FREE account (takes 30 seconds)")
    print("3. Verify your email")
    print("4. Go to: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("5. Copy your auth token")
    print()
    
    # Check if ngrok is already configured
    try:
        result = subprocess.run(['ngrok', 'config', 'check'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ngrok is already configured!")
            return True
    except:
        pass
    
    # Get auth token from user
    auth_token = input("🔑 Paste your auth token here: ").strip()
    
    if not auth_token:
        print("❌ No token provided. Please try again.")
        return False
    
    # Configure ngrok
    try:
        result = subprocess.run(['ngrok', 'config', 'add-authtoken', auth_token], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Auth token configured successfully!")
            print("🎉 You're ready to deploy your app!")
            return True
        else:
            print(f"❌ Error configuring token: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 EHM Akademi - Ngrok Setup")
    print("=" * 30)
    print()
    
    if setup_ngrok_auth():
        print()
        print("🎯 Setup complete! Now you can run:")
        print("   python app.py")
        print("   or")
        print("   Double-click start_live.bat")
    else:
        print()
        print("❌ Setup failed. Please try again.")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()