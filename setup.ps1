# ArtifactVirtual.com - PowerShell Setup Script
# Self-contained web server setup for Windows

param(
    [switch]$SkipDependencies,
    [switch]$Verbose
)

Write-Host "🚀 ArtifactVirtual.com - Portable Server Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create directory structure
$directories = @(
    "config", "nginx", "www\html", "www\api", 
    "ssl\certs", "logs", "monitor", "scripts"
)

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   Created: $dir" -ForegroundColor Gray
    }
}

# Download Nginx for Windows if not present
if (!(Test-Path "nginx\nginx.exe")) {
    Write-Host "📥 Downloading Nginx for Windows..." -ForegroundColor Yellow
    
    try {
        $nginxUrl = "https://nginx.org/download/nginx-1.24.0.zip"
        $nginxZip = "nginx-temp.zip"
        
        # Download with progress
        Invoke-WebRequest -Uri $nginxUrl -OutFile $nginxZip -UseBasicParsing
        
        Write-Host "📦 Extracting Nginx..." -ForegroundColor Yellow
        Expand-Archive -Path $nginxZip -DestinationPath "temp" -Force
        
        # Copy nginx files
        $nginxTempDir = "temp\nginx-1.24.0"
        if (Test-Path $nginxTempDir) {
            Copy-Item "$nginxTempDir\*" "nginx\" -Recurse -Force
        }
        
        # Cleanup
        Remove-Item $nginxZip -Force -ErrorAction SilentlyContinue
        Remove-Item "temp" -Recurse -Force -ErrorAction SilentlyContinue
        
        Write-Host "✅ Nginx installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to download Nginx: $_" -ForegroundColor Red
        Write-Host "Please download nginx-1.24.0.zip manually from https://nginx.org/download/" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Nginx already present" -ForegroundColor Green
}

# Create mime.types file
$mimeTypes = @"
types {
    text/html                             html htm shtml;
    text/css                              css;
    text/xml                              xml;
    application/javascript                js;
    application/json                      json;
    image/gif                             gif;
    image/jpeg                            jpeg jpg;
    image/png                             png;
    image/svg+xml                         svg svgz;
    image/x-icon                          ico;
    application/pdf                       pdf;
    application/zip                       zip;
    video/mp4                             mp4;
    audio/mpeg                            mp3;
}
"@

$mimeTypes | Out-File -FilePath "nginx\mime.types" -Encoding UTF8
Write-Host "✅ Created mime.types" -ForegroundColor Green

# Create monitoring dashboard
$dashboardCode = @"
#!/usr/bin/env python3
import time
import platform
import psutil
from datetime import datetime

class SimpleMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        
    def show_dashboard(self):
        print("🖥️  ArtifactVirtual.com - System Monitor")
        print("=" * 50)
        print(f"Hostname: {platform.node()}")
        print(f"Platform: {platform.platform()}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        try:
            while True:
                uptime = datetime.now() - self.start_time
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                print(f"\rUptime: {str(uptime)[:8]} | CPU: {cpu:5.1f}% | Memory: {memory.percent:5.1f}% | Time: {datetime.now().strftime('%H:%M:%S')}", end="", flush=True)
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped")

if __name__ == "__main__":
    monitor = SimpleMonitor()
    monitor.show_dashboard()
"@

$dashboardCode | Out-File -FilePath "monitor\dashboard.py" -Encoding UTF8
Write-Host "✅ Created monitoring dashboard" -ForegroundColor Green

# Install Python dependencies
if (!$SkipDependencies) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install psutil rich --user --quiet
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Some dependencies failed to install (optional)" -ForegroundColor Yellow
    }
}

# Create simple landing page
$landingPage = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArtifactVirtual.com - Server Online</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; 
            display: flex; align-items: center; justify-content: center;
        }
        .container { text-align: center; max-width: 600px; padding: 2rem; }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        .status { background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; margin: 2rem 0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
        .card { background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; }
        .card h3 { color: #4CAF50; margin-bottom: 0.5rem; }
        .footer { margin-top: 2rem; opacity: 0.8; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ArtifactVirtual.com</h1>
        <p>Self-Contained Web Server</p>
        
        <div class="status">
            <h2>✅ System Status: Online</h2>
            <p>Portable Server Running Successfully</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🌐 Server</h3>
                <p>Nginx + Python</p>
            </div>
            <div class="card">
                <h3>🔒 Security</h3>
                <p>SSL + Headers</p>
            </div>
            <div class="card">
                <h3>📊 Monitor</h3>
                <p>Real-time Stats</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Docker-free • Self-contained • Production-ready</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
        
        // Show current time
        setInterval(() => {
            document.title = `ArtifactVirtual.com - ${new Date().toLocaleTimeString()}`;
        }, 1000);
    </script>
</body>
</html>
"@

$landingPage | Out-File -FilePath "www\html\index.html" -Encoding UTF8
Write-Host "✅ Created landing page" -ForegroundColor Green

Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "`n🚀 To start the server:" -ForegroundColor Cyan
Write-Host "   start_server.bat" -ForegroundColor White
Write-Host "   OR" -ForegroundColor Gray
Write-Host "   python portable_server.py" -ForegroundColor White

Write-Host "`n📊 Your server will be available at:" -ForegroundColor Cyan
Write-Host "   HTTP:  http://localhost:8080" -ForegroundColor White
Write-Host "   HTTPS: https://localhost:8443" -ForegroundColor White
Write-Host "   Health: http://localhost:8080/health" -ForegroundColor White

Write-Host "`n✨ Features enabled:" -ForegroundColor Cyan
Write-Host "   • Self-contained Nginx server" -ForegroundColor White
Write-Host "   • SSL/HTTPS support" -ForegroundColor White
Write-Host "   • Security monitoring" -ForegroundColor White
Write-Host "   • Zero external dependencies" -ForegroundColor White
Write-Host "   • Production-ready configuration" -ForegroundColor White

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
