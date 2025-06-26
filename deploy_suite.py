#!/usr/bin/env python3
"""
Unified Deployment Script
Docker-free, self-contained deployment with AI automation
"""

import subprocess
import sys
import time
from pathlib import Path


def main():
    print("🚀 Reverse Ingress-Nginx Infrastructure Suite")
    print("=" * 55)
    
    base_dir = Path(__file__).parent.absolute()
    
    print("📋 Deployment Options:")
    print("1. 🌐 Start Portable Web Server")
    print("2. 📊 Launch Security Dashboard")
    print("3. 🤖 Start AI Automation Engine")
    print("4. 🔧 Full Stack Deploy (All Services)")
    print("5. 📱 Quick Health Check")
    print("0. Exit")
    
    choice = input("\nSelect option (0-5): ").strip()
    
    if choice == "1":
        print("\n🌐 Starting Portable Web Server...")
        subprocess.run([sys.executable, "portable_server.py"], cwd=base_dir)
        
    elif choice == "2":
        print("\n📊 Launching Security Dashboard...")
        subprocess.run([sys.executable, "dashboard_launcher.py"], cwd=base_dir)
        
    elif choice == "3":
        print("\n🤖 Starting AI Automation Engine...")
        subprocess.run([sys.executable, "ai_automation.py"], cwd=base_dir)
        
    elif choice == "4":
        print("\n🔧 Full Stack Deployment...")
        
        # Start web server in background
        print("Starting web server...")
        web_process = subprocess.Popen([sys.executable, "portable_server.py"], cwd=base_dir)
        time.sleep(5)
        
        # Start dashboard in background
        print("Starting security dashboard...")
        dashboard_process = subprocess.Popen([sys.executable, "dashboard_launcher.py"], cwd=base_dir)
        time.sleep(3)
        
        # Start AI automation
        print("Starting AI automation...")
        automation_process = subprocess.Popen([sys.executable, "ai_automation.py"], cwd=base_dir)
        
        print("\n✅ Full stack deployed!")
        print("🌐 Web: https://localhost:8443")
        print("📊 Dashboard: Check terminal")
        print("🤖 AI: Check automation logs")
        print("\nPress Ctrl+C to stop all services...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for process in [web_process, dashboard_process, automation_process]:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    process.kill()
        
    elif choice == "5":
        print("\n📱 Quick Health Check...")
        try:
            import requests
            response = requests.get("https://localhost:8443/health", verify=False, timeout=10)
            if response.status_code == 200:
                print("✅ Server is healthy!")
            else:
                print(f"⚠️ Server returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            print("💡 Try starting the server first (option 1)")
        
    elif choice == "0":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
