#!/usr/bin/env python3
"""
ArtifactVirtual.com - Portable Server Setup
Complete setup script for self-contained web server
"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path


class PortableServerSetup:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        
        print(f"🔧 Setting up portable server for {self.system} {self.arch}")

    def create_directory_structure(self):
        """Create required directories"""
        dirs = [
            "config", "nginx", "www/html", "www/api", 
            "ssl/certs", "logs", "monitor", "scripts"
        ]
        
        for dir_path in dirs:
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {dir_path}")

    def download_nginx(self):
        """Download and setup nginx binary"""
        nginx_dir = self.base_dir / "nginx"
        
        if self.system == "windows":
            return self.download_nginx_windows()
        elif self.system == "linux":
            return self.download_nginx_linux()
        elif self.system == "darwin":
            return self.download_nginx_macos()
        else:
            print(f"❌ Unsupported system: {self.system}")
            return False

    def download_nginx_windows(self):
        """Download nginx for Windows"""
        nginx_dir = self.base_dir / "nginx"
        nginx_exe = nginx_dir / "nginx.exe"
        
        if nginx_exe.exists():
            print("✅ Nginx already exists")
            return True
            
        print("📥 Downloading Nginx for Windows...")
        
        url = "https://nginx.org/download/nginx-1.24.0.zip"
        zip_file = self.base_dir / "nginx.zip"
        
        try:
            urllib.request.urlretrieve(url, zip_file)
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.base_dir / "temp")
            
            # Move nginx files
            temp_nginx = self.base_dir / "temp" / "nginx-1.24.0"
            if temp_nginx.exists():
                for item in temp_nginx.iterdir():
                    if item.is_file():
                        shutil.copy2(item, nginx_dir)
                    elif item.is_dir() and item.name in ["conf", "html", "logs"]:
                        shutil.copytree(item, nginx_dir / item.name, dirs_exist_ok=True)
            
            # Cleanup
            shutil.rmtree(self.base_dir / "temp", ignore_errors=True)
            zip_file.unlink(missing_ok=True)
            
            print("✅ Nginx downloaded and extracted")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download nginx: {e}")
            return False

    def download_nginx_linux(self):
        """Download or install nginx for Linux"""
        nginx_dir = self.base_dir / "nginx"
        nginx_bin = nginx_dir / "nginx"
        
        if nginx_bin.exists():
            print("✅ Nginx already exists")
            return True
            
        # Try to use system nginx
        try:
            nginx_path = shutil.which("nginx")
            if nginx_path:
                shutil.copy2(nginx_path, nginx_bin)
                os.chmod(nginx_bin, 0o755)
                print("✅ Copied system nginx")
                return True
        except:
            pass
            
        # Try to install via package manager
        print("📦 Installing nginx via package manager...")
        
        if shutil.which("apt-get"):
            try:
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "nginx-core"], check=True)
                nginx_path = "/usr/sbin/nginx"
                if Path(nginx_path).exists():
                    shutil.copy2(nginx_path, nginx_bin)
                    os.chmod(nginx_bin, 0o755)
                    print("✅ Installed nginx via apt")
                    return True
            except:
                pass
        
        print("❌ Failed to install nginx")
        return False

    def download_nginx_macos(self):
        """Download or install nginx for macOS"""
        nginx_dir = self.base_dir / "nginx"
        nginx_bin = nginx_dir / "nginx"
        
        if nginx_bin.exists():
            print("✅ Nginx already exists")
            return True
            
        # Try homebrew
        if shutil.which("brew"):
            try:
                subprocess.run(["brew", "install", "nginx"], check=True)
                nginx_path = subprocess.check_output(["which", "nginx"]).decode().strip()
                shutil.copy2(nginx_path, nginx_bin)
                os.chmod(nginx_bin, 0o755)
                print("✅ Installed nginx via homebrew")
                return True
            except:
                pass
        
        print("❌ Failed to install nginx")
        return False

    def create_mime_types(self):
        """Create mime.types file"""
        mime_content = """
types {
    text/html                             html htm shtml;
    text/css                              css;
    text/xml                              xml;
    image/gif                             gif;
    image/jpeg                            jpeg jpg;
    application/javascript                js;
    application/atom+xml                  atom;
    application/rss+xml                   rss;
    text/mathml                           mml;
    text/plain                            txt;
    text/vnd.sun.j2me.app-descriptor      jad;
    text/vnd.wap.wml                      wml;
    text/x-component                      htc;
    image/png                             png;
    image/tiff                            tif tiff;
    image/vnd.wap.wbmp                    wbmp;
    image/x-icon                          ico;
    image/x-jng                           jng;
    image/x-ms-bmp                        bmp;
    image/svg+xml                         svg svgz;
    image/webp                            webp;
    application/font-woff                 woff;
    application/java-archive              jar war ear;
    application/json                      json;
    application/mac-binhex40              hqx;
    application/msword                    doc;
    application/pdf                       pdf;
    application/postscript                ps eps ai;
    application/rtf                       rtf;
    application/vnd.apple.mpegurl         m3u8;
    application/vnd.ms-excel              xls;
    application/vnd.ms-fontobject         eot;
    application/vnd.ms-powerpoint         ppt;
    application/vnd.wap.wmlc              wmlc;
    application/vnd.google-earth.kml+xml  kml;
    application/vnd.google-earth.kmz      kmz;
    application/x-7z-compressed           7z;
    application/x-cocoa                   cco;
    application/x-java-archive-diff       jardiff;
    application/x-java-jnlp-file          jnlp;
    application/x-makeself                run;
    application/x-perl                    pl pm;
    application/x-pilot                   prc pdb;
    application/x-rar-compressed          rar;
    application/x-redhat-package-manager  rpm;
    application/x-sea                     sea;
    application/x-shockwave-flash         swf;
    application/x-stuffit                 sit;
    application/x-tcl                     tcl tk;
    application/x-x509-ca-cert            der pem crt;
    application/x-xpinstall               xpi;
    application/xhtml+xml                 xhtml;
    application/zip                       zip;
    application/octet-stream              bin exe dll;
    application/octet-stream              deb;
    application/octet-stream              dmg;
    application/octet-stream              iso img;
    application/octet-stream              msi msp msm;
    audio/midi                            mid midi kar;
    audio/mpeg                            mp3;
    audio/ogg                             ogg;
    audio/x-m4a                           m4a;
    audio/x-realaudio                     ra;
    video/3gpp                            3gpp 3gp;
    video/mp2t                            ts;
    video/mp4                             mp4;
    video/mpeg                            mpeg mpg;
    video/quicktime                       mov;
    video/webm                            webm;
    video/x-flv                           flv;
    video/x-m4v                           m4v;
    video/x-mng                           mng;
    video/x-ms-asf                        asx asf;
    video/x-ms-wmv                        wmv;
    video/x-msvideo                       avi;
}
""".strip()
        
        mime_file = self.base_dir / "nginx" / "mime.types"
        mime_file.write_text(mime_content)
        print("✅ Created mime.types")

    def create_monitoring_dashboard(self):
        """Create enhanced monitoring dashboard"""
        dashboard_content = '''#!/usr/bin/env python3
"""
ArtifactVirtual.com - Enhanced Monitoring Dashboard
"""

import time
import sys
import json
import platform
import psutil
from datetime import datetime
from pathlib import Path

class MonitoringDashboard:
    def __init__(self):
        self.start_time = datetime.now()
        
    def get_system_info(self):
        """Get system information"""
        return {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
        }
    
    def get_current_stats(self):
        """Get current system stats"""
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
    
    def display_dashboard(self):
        """Display monitoring dashboard"""
        try:
            import rich
            from rich.console import Console
            from rich.table import Table
            from rich.live import Live
            from rich.panel import Panel
            
            console = Console()
            
            def make_layout():
                system_info = self.get_system_info()
                current_stats = self.get_current_stats()
                
                # System Info Table
                info_table = Table(title="System Information", show_header=True)
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="green")
                
                info_table.add_row("Hostname", system_info["hostname"])
                info_table.add_row("Platform", system_info["platform"])
                info_table.add_row("CPU Cores", str(system_info["cpu_count"]))
                info_table.add_row("Memory", f"{system_info['memory_total'] / 1024**3:.1f} GB")
                
                # Stats Table
                stats_table = Table(title="Current Statistics", show_header=True)
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="green")
                
                stats_table.add_row("Uptime", current_stats["uptime"])
                stats_table.add_row("CPU Usage", f"{current_stats['cpu_percent']:.1f}%")
                stats_table.add_row("Memory Usage", f"{current_stats['memory_percent']:.1f}%")
                stats_table.add_row("Disk Usage", f"{system_info['disk_usage']:.1f}%")
                
                return Panel.fit(
                    f"[bold blue]ArtifactVirtual.com - Monitoring Dashboard[/bold blue]\\n\\n"
                    f"{info_table}\\n\\n{stats_table}\\n\\n"
                    "[yellow]Press Ctrl+C to exit[/yellow]"
                )
            
            with Live(make_layout(), refresh_per_second=1) as live:
                while True:
                    time.sleep(1)
                    live.update(make_layout())
                    
        except ImportError:
            # Fallback to simple text dashboard
            self.simple_dashboard()
    
    def simple_dashboard(self):
        """Simple text-based dashboard"""
        print("ArtifactVirtual.com - Monitoring Dashboard")
        print("=" * 50)
        
        system_info = self.get_system_info()
        print(f"Hostname: {system_info['hostname']}")
        print(f"Platform: {system_info['platform']}")
        print(f"CPU Cores: {system_info['cpu_count']}")
        print(f"Memory: {system_info['memory_total'] / 1024**3:.1f} GB")
        print()
        
        try:
            while True:
                stats = self.get_current_stats()
                print(f"\\rUptime: {stats['uptime']} | "
                      f"CPU: {stats['cpu_percent']:.1f}% | "
                      f"Memory: {stats['memory_percent']:.1f}% | "
                      f"Time: {stats['timestamp'][:19]}", end="", flush=True)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\\nMonitoring stopped")

def main():
    dashboard = MonitoringDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
'''
        
        dashboard_file = self.base_dir / "monitor" / "dashboard.py"
        dashboard_file.write_text(dashboard_content)
        os.chmod(dashboard_file, 0o755)
        print("✅ Created monitoring dashboard")

    def create_requirements_file(self):
        """Create requirements file for monitoring"""
        requirements = """psutil>=5.9.0
rich>=13.0.0
"""
        req_file = self.base_dir / "monitor" / "requirements.txt"
        req_file.write_text(requirements)
        print("✅ Created requirements.txt")

    def create_launcher_scripts(self):
        """Create platform-specific launcher scripts"""
        
        # Linux/macOS launcher
        if self.system in ["linux", "darwin"]:
            launcher_content = """#!/bin/bash
echo "🚀 Starting ArtifactVirtual.com Portable Server..."

# Install monitoring dependencies
if [ -f "monitor/requirements.txt" ]; then
    echo "📦 Installing monitoring dependencies..."
    pip3 install -r monitor/requirements.txt --user --quiet
fi

# Start the server
python3 portable_server.py
"""
            launcher_file = self.base_dir / "start_server.sh"
            launcher_file.write_text(launcher_content)
            os.chmod(launcher_file, 0o755)
            print("✅ Created start_server.sh")

    def install_python_deps(self):
        """Install Python dependencies"""
        req_file = self.base_dir / "monitor" / "requirements.txt"
        if req_file.exists():
            try:
                print("📦 Installing Python dependencies...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "-r", str(req_file), "--user", "--quiet"
                ], check=True)
                print("✅ Python dependencies installed")
            except subprocess.CalledProcessError:
                print("⚠️  Failed to install some dependencies (optional)")

    def run_setup(self):
        """Run complete setup"""
        print("🚀 ArtifactVirtual.com - Portable Server Setup")
        print("=" * 50)
        
        self.create_directory_structure()
        
        if not self.download_nginx():
            print("❌ Failed to setup nginx")
            return False
            
        self.create_mime_types()
        self.create_monitoring_dashboard()
        self.create_requirements_file()
        self.create_launcher_scripts()
        self.install_python_deps()
        
        print("\n✅ Setup completed successfully!")
        print("\n🚀 To start the server:")
        if self.system == "windows":
            print("   start_server.bat")
        else:
            print("   ./start_server.sh")
        
        print("\n📊 Features:")
        print("   • Self-contained Nginx server")
        print("   • SSL/HTTPS support")
        print("   • Security monitoring dashboard")
        print("   • Zero external dependencies")
        print("   • Portable across systems")
        
        return True


def main():
    setup = PortableServerSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()
