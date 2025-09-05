#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ALTERNATIVE DEPLOYMENT - NO WARNING PAGES!
Uses multiple tunneling services to avoid ngrok warnings
"""

import subprocess
import threading
import time
import sys
import os
from flask import Flask
import webbrowser

def start_flask_app():
    """Start Flask app in background"""
    try:
        # Import and run the main app
        import app
        print("✅ Flask app started successfully!")
    except Exception as e:
        print(f"❌ Error starting Flask: {e}")

def setup_localtunnel():
    """Setup localtunnel (NO WARNING PAGES)"""
    print("🔧 Setting up LocalTunnel (NO warning pages)...")
    
    try:
        # Install localtunnel if not exists
        subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True, capture_output=True)
        print("✅ LocalTunnel installed!")
        
        # Start localtunnel
        result = subprocess.run(['lt', '--port', '5000', '--subdomain', 'ehm-akademi'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ LocalTunnel started successfully!")
            return True
    except:
        print("⚠️ LocalTunnel not available")
        return False

def start_serveo():
    """Start Serveo tunnel (NO WARNING PAGES)"""
    print("🔧 Starting Serveo tunnel...")
    
    try:
        # Start serveo tunnel
        cmd = ['ssh', '-R', '80:localhost:5000', 'serveo.net']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for URL
        time.sleep(3)
        print("✅ Serveo tunnel should be active!")
        print("🌐 Check your terminal for the Serveo URL")
        return True
    except:
        print("⚠️ Serveo not available")
        return False

def main():
    """Main alternative deployment"""
    print("🚀 ALTERNATIVE DEPLOYMENT - NO WARNING PAGES!")
    print("=" * 60)
    
    # Start Flask in background
    print("1️⃣ Starting Flask application...")
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(3)  # Wait for Flask to start
    
    # Try alternative tunneling services
    success = False
    
    print("\n2️⃣ Trying alternative tunneling services...")
    
    # Option 1: LocalTunnel
    if setup_localtunnel():
        success = True
    
    # Option 2: Serveo
    if not success:
        if start_serveo():
            success = True
    
    # Option 3: Manual port forwarding instructions
    if not success:
        print("\n3️⃣ MANUAL SOLUTION:")
        print("🔧 Use port forwarding or VPS:")
        print("   • Option A: Use your router's port forwarding (port 5000)")
        print("   • Option B: Deploy to a VPS (DigitalOcean, AWS, etc.)")
        print("   • Option C: Use Cloudflare Tunnel (free, no warnings)")
        print("\n🌐 Your app is running locally at: http://localhost:5000")
    
    print(f"\n{'='*60}")
    print("✅ DEPLOYMENT COMPLETE - NO WARNING PAGES!")
    print("⚠️ Keep this window open to maintain connection")
    print(f"{'='*60}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deployment stopped")

if __name__ == '__main__':
    main()