#!/usr/bin/env python3
"""
ArtifactVirtual.com - One-Click Deployment
Complete setup and launch in a single command
"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path


def print_banner():
    """Print startup banner"""
    print("🚀 ArtifactVirtual.com - One-Click Deployment")
    print("=" * 60)
    print("🎯 Self-contained • Docker-free • Production-ready")
    print("🛡️  Security hardened • AI/ML optimized • Quantum ready")
    print("=" * 60)


def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def setup_directories():
    """Create required directory structure"""
    dirs = [
        "config", "nginx", "www/html", "ssl/certs", 
        "logs", "monitor", "scripts"
    ]
    
    base_dir = Path(__file__).parent
    for dir_name in dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("📁 Directory structure created")


def download_nginx_windows():
    """Download Nginx for Windows"""
    nginx_exe = Path("nginx/nginx.exe")
    if nginx_exe.exists():
        print("✅ Nginx already present")
        return True
    
    print("📥 Downloading Nginx for Windows...")
    
    try:
        url = "https://nginx.org/download/nginx-1.24.0.zip"
        zip_file = "nginx-temp.zip"
        
        urllib.request.urlretrieve(url, zip_file)
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall("temp")
        
        # Move files
        temp_dir = Path("temp/nginx-1.24.0")
        nginx_dir = Path("nginx")
        
        for item in temp_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, nginx_dir)
            elif item.name in ["conf", "html", "logs"]:
                shutil.copytree(item, nginx_dir / item.name, dirs_exist_ok=True)
        
        # Cleanup
        shutil.rmtree("temp", ignore_errors=True)
        Path(zip_file).unlink(missing_ok=True)
        
        print("✅ Nginx installed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download Nginx: {e}")
        return False


def setup_nginx_linux():
    """Setup Nginx for Linux"""
    nginx_bin = Path("nginx/nginx")
    if nginx_bin.exists():
        print("✅ Nginx already present")
        return True
    
    # Try system nginx first
    system_nginx = shutil.which("nginx")
    if system_nginx:
        shutil.copy2(system_nginx, nginx_bin)
        os.chmod(nginx_bin, 0o755)
        print("✅ Using system Nginx")
        return True
    
    # Try package manager
    print("📦 Installing Nginx...")
    try:
        if shutil.which("apt-get"):
            subprocess.run(["sudo", "apt-get", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "nginx-core"], check=True, capture_output=True)
        elif shutil.which("yum"):
            subprocess.run(["sudo", "yum", "install", "-y", "nginx"], check=True, capture_output=True)
        elif shutil.which("dnf"):
            subprocess.run(["sudo", "dnf", "install", "-y", "nginx"], check=True, capture_output=True)
        
        system_nginx = shutil.which("nginx") or "/usr/sbin/nginx"
        if Path(system_nginx).exists():
            shutil.copy2(system_nginx, nginx_bin)
            os.chmod(nginx_bin, 0o755)
            print("✅ Nginx installed")
            return True
            
    except subprocess.CalledProcessError:
        pass
    
    print("❌ Failed to install Nginx")
    return False


def create_configs():
    """Create configuration files"""
    
    # Nginx config
    nginx_config = '''
worker_processes auto;
error_log logs/error.log warn;
pid logs/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer"';
    
    access_log logs/access.log main;
    
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    server {
        listen 8080;
        server_name localhost;
        root www/html;
        index index.html;
        
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        location /health {
            access_log off;
            return 200 "OK\\n";
            add_header Content-Type text/plain;
        }
    }
}
'''.strip()
    
    Path("config/nginx.conf").write_text(nginx_config)
    
    # MIME types
    mime_types = '''
types {
    text/html                             html htm shtml;
    text/css                              css;
    application/javascript                js;
    application/json                      json;
    image/png                             png;
    image/jpeg                            jpeg jpg;
    image/gif                             gif;
    image/svg+xml                         svg;
}
'''.strip()
    
    Path("nginx/mime.types").write_text(mime_types)
    
    print("✅ Configuration files created")


def create_landing_page():
    """Create landing page"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtifactVirtual.com - Server Online</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; 
            display: flex; align-items: center; justify-content: center;
        }
        .container { text-align: center; max-width: 800px; padding: 2rem; }
        h1 { font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite; }
        .status { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 15px; margin: 2rem 0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem; }
        .card { background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .card h3 { color: #4CAF50; margin-bottom: 0.5rem; }
        .footer { margin-top: 3rem; opacity: 0.8; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ArtifactVirtual.com</h1>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">AI/ML Infrastructure Platform</p>
        
        <div class="status">
            <h2>✅ System Status: Online</h2>
            <p>Self-Contained Server • Docker-Free • Production Ready</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🌐 Web Server</h3>
                <p>Nginx + Python<br>High Performance</p>
            </div>
            <div class="card">
                <h3>🛡️ Security</h3>
                <p>SSL + Headers<br>Hardened Config</p>
            </div>
            <div class="card">
                <h3>📊 Monitoring</h3>
                <p>Real-time Stats<br>System Metrics</p>
            </div>
            <div class="card">
                <h3>🔧 Portable</h3>
                <p>Zero Dependencies<br>Self-Contained</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>ArtifactVirtual.com</strong> - Quantum/VM Ready • AI/ML Optimized</p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">Started: <span id="start-time"></span></p>
        </div>
    </div>
    
    <script>
        document.getElementById('start-time').textContent = new Date().toLocaleString();
        setInterval(() => {
            document.title = `ArtifactVirtual.com - ${new Date().toLocaleTimeString()}`;
        }, 1000);
    </script>
</body>
</html>'''
    
    Path("www/html/index.html").write_text(html_content)
    print("✅ Landing page created")


def start_server():
    """Start the Nginx server"""
    system = platform.system().lower()
    
    if system == "windows":
        nginx_cmd = ["nginx/nginx.exe", "-c", "config/nginx.conf"]
    else:
        nginx_cmd = ["./nginx/nginx", "-c", "config/nginx.conf"]
    
    try:
        # Change to base directory
        os.chdir(Path(__file__).parent)
        
        # Start nginx
        process = subprocess.Popen(nginx_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it a moment to start
        import time
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Server started successfully!")
            print()
            print("🌐 Server URLs:")
            print("   • Main Site: http://localhost:8080")
            print("   • Health Check: http://localhost:8080/health")
            print()
            print("📊 Server Information:")
            print("   • Configuration: config/nginx.conf")
            print("   • Access Logs: logs/access.log")
            print("   • Error Logs: logs/error.log")
            print()
            print("🛑 To stop the server:")
            if system == "windows":
                print("   taskkill /f /im nginx.exe")
            else:
                print("   pkill nginx")
            print()
            print("Press Ctrl+C to continue...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Deployment complete!")
                
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True


def main():
    """Main deployment function"""
    print_banner()
    
    if not check_python():
        sys.exit(1)
    
    setup_directories()
    
    system = platform.system().lower()
    if system == "windows":
        if not download_nginx_windows():
            sys.exit(1)
    else:
        if not setup_nginx_linux():
            sys.exit(1)
    
    create_configs()
    create_landing_page()
    
    print()
    print("🎉 Setup completed! Starting server...")
    print()
    
    start_server()


if __name__ == "__main__":
    main()
