# Reverse Ingress-Nginx Web Infrastructure - Complete Deployment Guide

Comprehensive deployment guide for enterprise-grade reverse proxy infrastructure: Development, Production, Docker-free, and CI/CD scenarios.

---

## Deployment Options

### Quick Start (Recommended)
**Use Case**: First-time users, development, testing
```bash
# Windows
start_ai_automation.bat

# Linux/macOS/PowerShell
python3 deploy_suite.py
```

### Production Deployment
**Use Case**: Live websites, production environments
- [Production Setup](#production-deployment-guide)
- Domain configuration, SSL certificates, performance tuning

### Docker Deployment (Legacy)
**Use Case**: Container environments, Kubernetes
- [Docker Setup](#docker-deployment-legacy)
- Container orchestration, Docker Compose

### Development Environment
**Use Case**: Local development, testing, customization
- [Development Setup](#development-environment)
- Hot reloading, debugging, custom configurations

---

## Quick Start Deployment

### Prerequisites
- Python 3.8+ (required)
- Node.js 18+ (for AI automation)
- 10MB free disk space
- Ports 8080, 8443, 8444 available

### Option 1: Automated (Windows)
```cmd
# Clone repository
git clone <your-repo>
cd core/cert-nginx

# Run interactive launcher
start_ai_automation.bat
# Select option 1 for full deployment

# Infrastructure endpoints:
# Web: http://localhost:8080
# SSL: https://localhost:8443  
# AI Dashboard: automation_logs/dashboard.html
```

### Option 2: Automated (Linux/macOS)
```bash
# Clone and deploy
git clone <your-repo> && cd core/cert-nginx
python3 deploy_suite.py

# Or step-by-step
python3 setup.py                 # Install dependencies
python3 portable_server.py       # Start web server
python3 dashboard_launcher.py    # Start monitoring (new terminal)
node automation_scripts/orchestrator_fixed.js dashboard  # Start AI (new terminal)
```

### Option 3: PowerShell (Advanced)
```powershell
# With parameters
.\start_ai_automation.ps1 dashboard -Verbose

# Individual services
.\start_ai_automation.ps1 performance
.\start_ai_automation.ps1 security -Headless
```

### Verification
```bash
# Check all services
curl http://localhost:8080/health    # Web server
ps aux | grep python                 # Security monitoring
ps aux | grep node                   # AI automation

# Open dashboards
# Security: Check terminal output
# AI: Open automation_logs/dashboard.html in browser
```

---

## Production Deployment Guide

### Phase 1: Server Preparation

**1. Server Requirements**
- OS: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+
- RAM: 2GB minimum, 4GB recommended
- CPU: 2 cores minimum, 4 cores recommended  
- Storage: 10GB minimum, 50GB recommended
- Network: Public IP, domains pointing to server

**2. Domain Setup**
```bash
# Update DNS records
# A record: artifactvirtual.com -> YOUR_SERVER_IP
# A record: www.artifactvirtual.com -> YOUR_SERVER_IP

# Verify DNS propagation
nslookup artifactvirtual.com
```

**3. Firewall Configuration**
```bash
# Ubuntu/Debian
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

### Phase 2: Application Deployment

**1. Install Dependencies**
```bash
# Install Python 3.8+
sudo apt update && sudo apt install python3 python3-pip -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Verify versions
python3 --version  # Should be 3.8+
node --version     # Should be 18+
```

**2. Deploy Application**
```bash
# Clone repository
git clone <your-repo>
cd core/cert-nginx

# Install Python dependencies
pip3 install -r monitor_requirements.txt

# Install Node.js dependencies
npm install

# Generate production SSL certificates
python3 setup.py --production --domain artifactvirtual.com

# Start production services
python3 deploy_suite.py --production
```

**3. Production Configuration**
```bash
# Edit production config
nano automation_config/config.json

# Update domains and SSL paths
{
    "targets": {
        "production": "https://artifactvirtual.com",
        "health": "https://artifactvirtual.com/health"
    },
    "ssl": {
        "cert_path": "/etc/ssl/certs/artifactvirtual.com.crt",
        "key_path": "/etc/ssl/private/artifactvirtual.com.key"
    }
}
```

### Phase 3: Process Management

**1. Systemd Services (Linux)**
```bash
# Create web server service
sudo tee /etc/systemd/system/artifactvirtual-web.service << EOF
[Unit]
Description=ArtifactVirtual Web Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cert-nginx
ExecStart=/usr/bin/python3 portable_server.py --production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring service
sudo tee /etc/systemd/system/artifactvirtual-monitor.service << EOF
[Unit]
Description=ArtifactVirtual Security Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cert-nginx
ExecStart=/usr/bin/python3 security_monitor.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl enable artifactvirtual-web artifactvirtual-monitor
sudo systemctl start artifactvirtual-web artifactvirtual-monitor
```

**2. Windows Services**
```cmd
# Install as Windows service using NSSM
# Download NSSM from https://nssm.cc/

# Install web server service
nssm install ArtifactVirtualWeb "C:\Python39\python.exe" "C:\path\to\portable_server.py --production"
nssm set ArtifactVirtualWeb AppDirectory "C:\path\to\cert-nginx"
nssm start ArtifactVirtualWeb

# Install monitoring service
nssm install ArtifactVirtualMonitor "C:\Python39\python.exe" "C:\path\to\security_monitor.py --daemon"
nssm start ArtifactVirtualMonitor
```

### Phase 4: SSL Certificate Setup

**1. Let's Encrypt (Recommended)**
```bash
# Install certbot
sudo apt install certbot -y

# Generate certificates
sudo certbot certonly --standalone \
    -d artifactvirtual.com \
    -d www.artifactvirtual.com \
    --email admin@artifactvirtual.com \
    --agree-tos \
    --non-interactive

# Setup auto-renewal
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

**2. Custom SSL Certificates**
```bash
# Copy your certificates
sudo cp your-domain.crt /etc/ssl/certs/artifactvirtual.com.crt
sudo cp your-domain.key /etc/ssl/private/artifactvirtual.com.key
sudo chmod 644 /etc/ssl/certs/artifactvirtual.com.crt
sudo chmod 600 /etc/ssl/private/artifactvirtual.com.key
```

### Phase 5: Performance Optimization

**1. Nginx Configuration**
```nginx
# Edit data/nginx/artifactvirtual.com.conf
server {
        listen 443 ssl http2;
        server_name artifactvirtual.com www.artifactvirtual.com;
        
        # Performance optimizations
        worker_processes auto;
        worker_connections 1024;
        keepalive_timeout 65;
        
        # Caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
        }
        
        # Compression
        gzip on;
        gzip_comp_level 6;
        gzip_types text/plain text/css application/json application/javascript;
}
```

**2. System Performance**
```bash
# Optimize kernel parameters
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
sysctl -p

# Increase file descriptor limits
echo '* soft nofile 65535' >> /etc/security/limits.conf
echo '* hard nofile 65535' >> /etc/security/limits.conf
```

---

Deployment complete. Your ArtifactVirtual.com infrastructure is now operational and ready for production use.
