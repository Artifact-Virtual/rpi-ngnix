#!/bin/bash

echo "🚀 Installing Portable Nginx Server..."

# Detect platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

echo "📋 Detected: $PLATFORM $ARCH"

# Create directory structure
mkdir -p nginx config www/html www/api ssl/certs logs monitor scripts

# Download portable Nginx binary based on platform
download_nginx() {
    case $PLATFORM in
        "Linux")
            if [ "$ARCH" = "x86_64" ]; then
                echo "📥 Downloading Nginx for Linux x64..."
                wget -O nginx/nginx https://github.com/nginx/nginx/releases/download/release-1.25.3/nginx-linux-x64
            elif [ "$ARCH" = "aarch64" ]; then
                echo "📥 Downloading Nginx for Linux ARM64..."
                wget -O nginx/nginx https://github.com/nginx/nginx/releases/download/release-1.25.3/nginx-linux-arm64
            fi
            ;;
        "Darwin")
            echo "📥 Downloading Nginx for macOS..."
            curl -L -o nginx/nginx https://github.com/nginx/nginx/releases/download/release-1.25.3/nginx-macos
            ;;
        "MINGW"*|"CYGWIN"*|"MSYS"*)
            echo "📥 Downloading Nginx for Windows..."
            curl -L -o nginx/nginx.exe https://nginx.org/download/nginx-1.25.3.zip
            ;;
        *)
            echo "❌ Unsupported platform: $PLATFORM"
            echo "📦 Installing via package manager..."
            install_via_package_manager
            ;;
    esac
}

# Fallback: Install via package manager
install_via_package_manager() {
    if command -v apt-get >/dev/null; then
        echo "📦 Installing via apt..."
        sudo apt-get update && sudo apt-get install -y nginx-core
        cp /usr/sbin/nginx nginx/
    elif command -v yum >/dev/null; then
        echo "📦 Installing via yum..."
        sudo yum install -y nginx
        cp /usr/sbin/nginx nginx/
    elif command -v brew >/dev/null; then
        echo "📦 Installing via Homebrew..."
        brew install nginx
        cp /opt/homebrew/bin/nginx nginx/ || cp /usr/local/bin/nginx nginx/
    else
        echo "❌ No package manager found. Please install Nginx manually."
        exit 1
    fi
}

# Try downloading portable binary first
download_nginx

# If download failed, use package manager
if [ ! -f "nginx/nginx" ] && [ ! -f "nginx/nginx.exe" ]; then
    echo "⚠️ Portable binary download failed, using package manager..."
    install_via_package_manager
fi

# Make executable
chmod +x nginx/nginx* 2>/dev/null

# Download mime.types
echo "📥 Downloading MIME types..."
curl -s -o nginx/mime.types https://raw.githubusercontent.com/nginx/nginx/master/conf/mime.types

# Create basic Nginx configuration
cat > config/nginx.conf << 'EOF'
user nobody;
worker_processes auto;
error_log logs/error.log;
pid nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    include nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log logs/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    server {
        listen 80;
        listen 443 ssl http2;
        server_name artifactvirtual.com localhost;
        root www/html;
        index index.html index.htm;
        
        # SSL configuration
        ssl_certificate ssl/certs/server.crt;
        ssl_certificate_key ssl/certs/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers for HTTPS
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        
        # Rate limiting
        limit_req zone=general burst=20 nodelay;
        
        # Main site
        location / {
            try_files $uri $uri/ /index.html;
            expires 1d;
        }
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }
        
        # Monitoring endpoint (restricted)
        location /monitor {
            allow 127.0.0.1;
            deny all;
            proxy_pass http://127.0.0.1:9000;
        }
        
        # Deny hidden files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
        
        # Error pages
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
    }
}
EOF

# Create SSL certificate generation script
cat > ssl/generate.sh << 'EOF'
#!/bin/bash
DOMAIN=${1:-artifactvirtual.com}
mkdir -p certs

echo "🔐 Generating SSL certificate for $DOMAIN..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/server.key \
    -out certs/server.crt \
    -subj "/C=US/ST=CA/L=San Francisco/O=ArtifactVirtual/CN=$DOMAIN"

chmod 600 certs/server.key
chmod 644 certs/server.crt

echo "✅ SSL certificate generated!"
EOF
chmod +x ssl/generate.sh

# Create basic HTML page
cat > www/html/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtifactVirtual - Portable Server</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        .container { max-width: 600px; margin: 0 auto; }
        .status { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ArtifactVirtual</h1>
        <p class="status">✅ Portable Server Running</p>
        <p>Zero dependencies. Fully self-contained.</p>
        <p><a href="/health">Health Check</a> | <a href="/monitor">Monitor (Local Only)</a></p>
    </div>
</body>
</html>
EOF

# Create startup script
cat > scripts/start_server.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ArtifactVirtual Portable Server..."

# Check if SSL certificates exist
if [ ! -f "ssl/certs/server.crt" ]; then
    echo "🔐 Generating SSL certificates..."
    ./ssl/generate.sh
fi

# Start Nginx
echo "🌐 Starting Nginx..."
if [ -f "nginx/nginx.exe" ]; then
    ./nginx/nginx.exe -c ../config/nginx.conf
else
    ./nginx/nginx -c config/nginx.conf
fi

# Check if started successfully
if [ $? -eq 0 ]; then
    echo "✅ Server started successfully!"
    echo "🌐 Access: http://localhost"
    echo "🔒 HTTPS: https://localhost"
    echo "📊 Monitor: python3 monitor/dashboard.py"
else
    echo "❌ Failed to start server"
    exit 1
fi
EOF
chmod +x scripts/start_server.sh

# Create stop script
cat > scripts/stop_server.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping ArtifactVirtual Server..."

if [ -f "nginx.pid" ]; then
    PID=$(cat nginx.pid)
    kill $PID
    echo "✅ Server stopped"
else
    echo "⚠️ No PID file found"
fi
EOF
chmod +x scripts/stop_server.sh

# Create status script
cat > scripts/status.sh << 'EOF'
#!/bin/bash
echo "📊 Server Status:"

if [ -f "nginx.pid" ]; then
    PID=$(cat nginx.pid)
    if ps -p $PID > /dev/null; then
        echo "✅ Nginx running (PID: $PID)"
    else
        echo "❌ Nginx not running (stale PID file)"
    fi
else
    echo "❌ Nginx not running"
fi

echo "📁 Disk usage: $(du -sh . | cut -f1)"
echo "📈 Log size: $(du -sh logs/ | cut -f1 2>/dev/null || echo '0')"
EOF
chmod +x scripts/status.sh

# Create Python monitoring requirements
cat > monitor/requirements.txt << 'EOF'
rich>=13.7.0
psutil>=5.9.0
requests>=2.31.0
EOF

# Install Python dependencies if Python is available
if command -v python3 >/dev/null; then
    echo "🐍 Installing Python monitoring dependencies..."
    python3 -m pip install -r monitor/requirements.txt --user
fi

# Generate SSL certificate
echo "🔐 Generating SSL certificate..."
./ssl/generate.sh

echo "✅ Installation complete!"
echo ""
echo "🚀 To start the server:"
echo "   ./scripts/start_server.sh"
echo ""
echo "📊 To monitor:"
echo "   python3 monitor/dashboard.py"
echo ""
echo "🛑 To stop:"
echo "   ./scripts/stop_server.sh"
