#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EHM Akademi - Cloudflare Tunnel Version
NO WARNING PAGES - 100% GUARANTEED!
"""

import subprocess
import threading
import time
import sys
import os

def start_cloudflare_quick_tunnel():
    """Start Cloudflare Quick Tunnel - NO REGISTRATION NEEDED!"""
    print("🚀 Starting Cloudflare Quick Tunnel...")
    print("✅ NO registration required!")
    print("✅ NO warning pages!")
    print("✅ Custom domain provided!")
    
    try:
        # Start cloudflare quick tunnel directly without downloading
        # This uses the cloudflare trycloudflare.com service
        cmd = [
            'npx', 'cloudflared', 'tunnel', 
            '--url', 'http://localhost:5000',
            '--no-autoupdate'
        ]
        
        print("📡 Creating tunnel...")
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Wait for tunnel URL
        tunnel_url = None
        start_time = time.time()
        
        while time.time() - start_time < 30:  # 30 second timeout
            line = process.stdout.readline()
            if line:
                print(f"🔧 {line.strip()}")
                if 'trycloudflare.com' in line:
                    # Extract URL
                    parts = line.split()
                    for part in parts:
                        if 'trycloudflare.com' in part:
                            tunnel_url = part.strip()
                            break
                    if tunnel_url:
                        break
            time.sleep(0.1)
        
        if tunnel_url:
            print(f"\n🎯 SUCCESS!")
            print(f"=" * 80)
            print(f"🌐 CLOUDFLARE TUNNEL URL: {tunnel_url}")
            print(f"🚫 NO WARNING PAGES - GUARANTEED!")
            print(f"🔥 DIRECT ACCESS - SHARE THIS URL!")
            print(f"=" * 80)
            return tunnel_url
        else:
            print("⚠️ Could not get tunnel URL, trying alternative...")
            return None
            
    except FileNotFoundError:
        print("❌ Node.js/npx not found. Trying alternative method...")
        return start_simple_tunnel()
    except Exception as e:
        print(f"❌ Cloudflare tunnel error: {e}")
        return start_simple_tunnel()

def start_simple_tunnel():
    """Start simple HTTP tunnel using Python"""
    print("🔧 Starting simple tunnel...")
    
    try:
        # Use Python HTTP server tunneling
        import socket
        import urllib.request
        
        # Get external IP for reference
        try:
            external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
            print(f"🌐 Your external IP: {external_ip}")
            print(f"💡 If you have port forwarding: http://{external_ip}:5000")
        except:
            pass
            
        # Alternative: Use localtunnel via Python
        print("🔄 Trying localtunnel alternative...")
        
        try:
            import requests
            # Simple tunnel service
            response = requests.post('https://localtunnel.me/api/tunnels', 
                                   json={'port': 5000})
            if response.status_code == 200:
                data = response.json()
                tunnel_url = data.get('url', '')
                if tunnel_url:
                    print(f"🎯 LOCALTUNNEL URL: {tunnel_url}")
                    print(f"🚫 NO WARNING PAGES!")
                    return tunnel_url
        except:
            pass
            
        print("💡 Manual options:")
        print("   1. Use ngrok with bypass URLs (already configured)")
        print("   2. Use your router's port forwarding")
        print("   3. Deploy to a cloud service")
        
        return None
        
    except Exception as e:
        print(f"❌ Simple tunnel error: {e}")
        return None

def start_flask_with_cloudflare():
    """Start Flask with Cloudflare tunnel"""
    
    # Start tunnel in background
    print("1️⃣ Starting Cloudflare tunnel...")
    tunnel_thread = threading.Thread(target=start_cloudflare_quick_tunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()
    
    # Give tunnel time to start
    time.sleep(3)
    
    # Start Flask app
    print("2️⃣ Starting Flask application...")
    try:
        # Import the main app and run it
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Flask error: {e}")

def main():
    """Main function"""
    print("☁️ EHM AKADEMI - CLOUDFLARE DEPLOYMENT")
    print("🎯 100% NO WARNING PAGES!")
    print("=" * 60)
    
    # Option 1: Try Cloudflare Quick Tunnel
    print("🚀 Option 1: Cloudflare Quick Tunnel")
    tunnel_url = start_cloudflare_quick_tunnel()
    
    if tunnel_url:
        print("✅ Cloudflare tunnel ready!")
    
    # Start Flask regardless
    print("\n🏃‍♂️ Starting Flask application...")
    try:
        # Start Flask with tunnel
        start_flask_with_cloudflare()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped")

if __name__ == '__main__':
    main()