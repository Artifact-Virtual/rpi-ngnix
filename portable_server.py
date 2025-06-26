#!/usr/bin/env python3
"""
Reverse Ingress-Nginx Infrastructure - Portable Server Launcher
Self-contained, dependency-free web server with monitoring dashboard
"""

import sys
import time
import signal
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional


class PortableServer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.config_dir = self.base_dir / "config"
        self.nginx_dir = self.base_dir / "nginx"
        self.www_dir = self.base_dir / "www"
        self.ssl_dir = self.base_dir / "ssl"
        self.logs_dir = self.base_dir / "logs"
        self.monitor_dir = self.base_dir / "monitor"
        
        self.nginx_process = None
        self.monitor_process = None
        self.is_running = False
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        self.logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_dependencies(self) -> bool:
        """Check if all required files and directories exist"""
        required_dirs = [
            self.config_dir,
            self.nginx_dir,
            self.www_dir,
            self.ssl_dir,
            self.logs_dir
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path))
        
        if missing_dirs:
            self.logger.error(f"Missing directories: {missing_dirs}")
            self.logger.info("Run './setup.py' first to initialize the server")
            return False
        
        # Check for nginx binary
        nginx_binary = self.get_nginx_binary()
        if not nginx_binary or not Path(nginx_binary).exists():
            self.logger.error("Nginx binary not found")
            return False
            
        return True

    def get_nginx_binary(self) -> Optional[str]:
        """Get the appropriate nginx binary for the current platform"""
        system = platform.system().lower()
        
        if system == "windows":
            return str(self.nginx_dir / "nginx.exe")
        else:
            return str(self.nginx_dir / "nginx")

    def generate_nginx_config(self):
        """Generate nginx configuration"""
        config_content = f"""
# ArtifactVirtual.com - Portable Nginx Configuration
worker_processes auto;
error_log {self.logs_dir}/error.log warn;
pid {self.logs_dir}/nginx.pid;

events {{
    worker_connections 1024;
    use {'epoll' if platform.system() != 'Windows' else 'select'};
}}

http {{
    include       mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log {self.logs_dir}/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 100M;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=static:10m rate=50r/s;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Main Server Block
    server {{
        listen 8080;
        listen 8443 ssl http2;
        server_name localhost artifactvirtual.com;
        
        root {self.www_dir}/html;
        index index.html index.htm;
        
        # SSL Configuration
        ssl_certificate {self.ssl_dir}/certs/server.crt;
        ssl_certificate_key {self.ssl_dir}/certs/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Static Files
        location / {{
            try_files $uri $uri/ /index.html;
            limit_req zone=static burst=20 nodelay;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
                expires 1y;
                add_header Cache-Control "public, immutable";
            }}
        }}
        
        # API Endpoints
        location /api/ {{
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://127.0.0.1:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
        
        # Health Check
        location /health {{
            access_log off;
            return 200 "OK\\n";
            add_header Content-Type text/plain;
        }}
        
        # Monitoring Dashboard (Internal)
        location /monitor {{
            allow 127.0.0.1;
            deny all;
            proxy_pass http://127.0.0.1:8001/;
        }}
    }}
}}
"""
        
        config_file = self.config_dir / "nginx.conf"
        config_file.write_text(config_content.strip())
        self.logger.info(f"Generated nginx config: {config_file}")

    def generate_ssl_certificates(self):
        """Generate self-signed SSL certificates"""
        cert_dir = self.ssl_dir / "certs"
        cert_dir.mkdir(exist_ok=True)
        
        cert_file = cert_dir / "server.crt"
        key_file = cert_dir / "server.key"
        
        if cert_file.exists() and key_file.exists():
            self.logger.info("SSL certificates already exist")
            return
        
        # Generate self-signed certificate
        openssl_cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_file),
            "-out", str(cert_file),
            "-days", "365", "-nodes",
            "-subj", "/C=US/ST=CA/L=SF/O=ArtifactVirtual/CN=localhost"
        ]
        
        try:
            subprocess.run(openssl_cmd, check=True, capture_output=True)
            self.logger.info(f"Generated SSL certificates: {cert_dir}")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Failed to generate SSL certificates: {e}")
            self.logger.info("Continuing without SSL...")

    def create_landing_page(self):
        """Create a simple landing page"""
        html_dir = self.www_dir / "html"
        html_dir.mkdir(exist_ok=True)
        
        index_html = html_dir / "index.html"
        if index_html.exists():
            return
            
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtifactVirtual.com - AI/ML Infrastructure</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; display: flex;
            align-items: center; justify-content: center;
        }
        .container { text-align: center; max-width: 800px; padding: 2rem; }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }
        .status { background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem; }
        .metric { background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; }
        .metric h3 { color: #4CAF50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ArtifactVirtual.com</h1>
        <p>AI/ML Infrastructure - Portable Server Running</p>
        <div class="status">
            <h2>✅ System Status: Online</h2>
            <p>Portable Nginx Server | Security Monitoring Active</p>
        </div>
        <div class="metrics">
            <div class="metric">
                <h3>Server</h3>
                <p>Nginx + Python</p>
            </div>
            <div class="metric">
                <h3>Security</h3>
                <p>SSL + Headers</p>
            </div>
            <div class="metric">
                <h3>Monitoring</h3>
                <p>Real-time Dashboard</p>
            </div>
        </div>
    </div>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""
        
        index_html.write_text(html_content)
        self.logger.info(f"Created landing page: {index_html}")

    def start_nginx(self):
        """Start nginx server"""
        nginx_binary = self.get_nginx_binary()
        config_file = self.config_dir / "nginx.conf"
        
        cmd = [nginx_binary, "-c", str(config_file)]
        
        try:
            self.nginx_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir)
            )
            self.logger.info(f"Started Nginx server (PID: {self.nginx_process.pid})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Nginx: {e}")
            return False

    def start_monitor(self):
        """Start monitoring dashboard"""
        monitor_script = self.monitor_dir / "dashboard.py"
        if not monitor_script.exists():
            self.logger.warning("Monitoring dashboard not found")
            return False
            
        try:
            self.monitor_process = subprocess.Popen([
                sys.executable, str(monitor_script)
            ], cwd=str(self.base_dir))
            self.logger.info(f"Started monitoring dashboard (PID: {self.monitor_process.pid})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return False

    def stop_all(self):
        """Stop all processes"""
        self.is_running = False
        
        if self.nginx_process:
            try:
                self.nginx_process.terminate()
                self.nginx_process.wait(timeout=10)
                self.logger.info("Stopped Nginx server")
            except:
                self.nginx_process.kill()
                
        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=5)
                self.logger.info("Stopped monitoring dashboard")
            except:
                self.monitor_process.kill()

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)

    def start(self):
        """Start the complete server stack"""
        print("🚀 ArtifactVirtual.com - Portable Server")
        print("=" * 50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependencies check failed!")
            return False
        
        # Generate configurations
        self.generate_nginx_config()
        self.generate_ssl_certificates()
        self.create_landing_page()
        
        # Start services
        print("🔧 Starting services...")
        
        if not self.start_nginx():
            print("❌ Failed to start Nginx")
            return False
            
        self.start_monitor()  # Optional, continue if fails
        
        self.is_running = True
        
        print("✅ Server started successfully!")
        print(f"🌐 Landing Page: http://localhost:8080")
        print(f"🔒 SSL Version: https://localhost:8443")
        print(f"📊 Health Check: http://localhost:8080/health")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep running
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
        
        return True

def main():
    """Main entry point"""
    server = PortableServer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "setup":
            print("Setting up portable server...")
            # Run setup logic here
        elif command == "stop":
            print("Stopping server...")
            # Stop logic here
        else:
            print(f"Unknown command: {command}")
            print("Usage: python portable_server.py [setup|stop]")
    else:
        server.start()

if __name__ == "__main__":
    main()
