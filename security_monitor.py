#!/usr/bin/env python3
"""
ArtifactVirtual Security Monitoring Dashboard
Advanced cybersecurity monitoring with beautiful CLI visualization
"""

import asyncio
import time
import json
import subprocess
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.gauge import Gauge
from rich.text import Text
from rich.align import Align
from rich import box
from rich.columns import Columns
from rich.tree import Tree


@dataclass
class SecurityMetrics:
    failed_logins: int = 0
    suspicious_ips: List[str] = None
    active_connections: int = 0
    ssl_certificate_days: int = 0
    rate_limit_hits: int = 0
    blocked_requests: int = 0
    
    def __post_init__(self):
        if self.suspicious_ips is None:
            self.suspicious_ips = []


@dataclass
class SystemMetrics:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    network_in: int = 0
    network_out: int = 0
    load_average: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class ServiceMetrics:
    nginx_status: str = "unknown"
    nginx_requests: int = 0
    nginx_errors: int = 0
    landing_page_status: str = "unknown"
    backend_api_status: str = "unknown"
    certbot_status: str = "unknown"
    response_times: Dict[str, float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = {}


class SecurityMonitor:
    def __init__(self):
        self.console = Console()
        self.security_metrics = SecurityMetrics()
        self.system_metrics = SystemMetrics()
        self.service_metrics = ServiceMetrics()
        self.start_time = time.time()
        self.alert_threshold = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0,
            'failed_logins': 10,
            'response_time': 2.0
        }
        
    async def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            self.system_metrics.cpu_percent = psutil.cpu_percent(interval=1)
            self.system_metrics.memory_percent = psutil.virtual_memory().percent
            self.system_metrics.disk_percent = psutil.disk_usage('/').percent
            
            net_io = psutil.net_io_counters()
            self.system_metrics.network_in = net_io.bytes_recv
            self.system_metrics.network_out = net_io.bytes_sent
            
            self.system_metrics.load_average = psutil.getloadavg()
        except Exception as e:
            self.console.print(f"[red]Error collecting system metrics: {e}[/red]")
    
    async def collect_security_metrics(self):
        """Collect security-related metrics"""
        try:
            # Check for failed login attempts (example from auth.log)
            failed_logins = await self.get_failed_logins()
            self.security_metrics.failed_logins = failed_logins
            
            # Get suspicious IPs from nginx logs
            suspicious_ips = await self.get_suspicious_ips()
            self.security_metrics.suspicious_ips = suspicious_ips
            
            # Check SSL certificate expiration
            ssl_days = await self.get_ssl_certificate_days()
            self.security_metrics.ssl_certificate_days = ssl_days
            
            # Check rate limiting
            rate_limits = await self.get_rate_limit_hits()
            self.security_metrics.rate_limit_hits = rate_limits
            
        except Exception as e:
            self.console.print(f"[red]Error collecting security metrics: {e}[/red]")
    
    async def collect_service_metrics(self):
        """Collect service status and performance metrics"""
        try:
            # Check Docker containers
            containers = await self.get_docker_status()
            self.service_metrics.nginx_status = containers.get('nginx', 'unknown')
            self.service_metrics.landing_page_status = containers.get('landing-page', 'unknown')
            self.service_metrics.backend_api_status = containers.get('backend-api', 'unknown')
            self.service_metrics.certbot_status = containers.get('certbot', 'unknown')
            
            # Check response times
            response_times = await self.check_response_times()
            self.service_metrics.response_times = response_times
            
        except Exception as e:
            self.console.print(f"[red]Error collecting service metrics: {e}[/red]")
    
    async def get_failed_logins(self) -> int:
        """Get failed login attempts from logs"""
        try:
            result = subprocess.run(
                ["docker-compose", "exec", "-T", "nginx", "grep", "-c", "401", "/var/log/nginx/access.log"],
                capture_output=True, text=True, timeout=5
            )
            return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        except:
            return 0
    
    async def get_suspicious_ips(self) -> List[str]:
        """Get suspicious IP addresses from nginx logs"""
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "nginx", "awk",
                "($9 ~ /4[0-9][0-9]/) { print $1 }", "/var/log/nginx/access.log"
            ], capture_output=True, text=True, timeout=5)
            ips = result.stdout.strip().split('\n') if result.stdout.strip() else []
            return list(set(ips))[:10]  # Return top 10 unique IPs
        except:
            return []
    
    async def get_ssl_certificate_days(self) -> int:
        """Get SSL certificate expiration days"""
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "certbot",
                "certbot", "certificates", "--cert-name", "artifactvirtual.com"
            ], capture_output=True, text=True, timeout=10)
            
            # Parse certificate expiration (simplified)
            if "VALID:" in result.stdout:
                return 30  # Placeholder - would parse actual date
            return 0
        except:
            return 0
    
    async def get_rate_limit_hits(self) -> int:
        """Get rate limiting hits"""
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "nginx",
                "grep", "-c", "limiting requests", "/var/log/nginx/error.log"
            ], capture_output=True, text=True, timeout=5)
            return int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
        except:
            return 0
    
    async def get_docker_status(self) -> Dict[str, str]:
        """Get Docker container status"""
        try:
            result = subprocess.run([
                "docker-compose", "ps", "--format", "json"
            ], capture_output=True, text=True, timeout=10)
            
            containers = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        service = data.get('Service', '')
                        state = data.get('State', 'unknown')
                        containers[service] = 'healthy' if state == 'running' else 'unhealthy'
                    except json.JSONDecodeError:
                        continue
            return containers
        except:
            return {}
    
    async def check_response_times(self) -> Dict[str, float]:
        """Check response times for endpoints"""
        endpoints = {
            'landing_page': 'https://artifactvirtual.com',
            'health_check': 'https://artifactvirtual.com/health',
            'api': 'https://artifactvirtual.com/api/health'
        }
        
        response_times = {}
        for name, url in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5, verify=False)
                response_time = time.time() - start_time
                response_times[name] = response_time
            except:
                response_times[name] = 999.0  # Timeout/error
        
        return response_times
    
    def create_system_panel(self) -> Panel:
        """Create system metrics panel"""
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", width=12)
        table.add_column("Value", style="green", width=15)
        table.add_column("Status", style="yellow", width=10)
        
        # CPU
        cpu_status = "🔴 HIGH" if self.system_metrics.cpu_percent > self.alert_threshold['cpu'] else "🟢 OK"
        table.add_row("CPU Usage", f"{self.system_metrics.cpu_percent:.1f}%", cpu_status)
        
        # Memory
        mem_status = "🔴 HIGH" if self.system_metrics.memory_percent > self.alert_threshold['memory'] else "🟢 OK"
        table.add_row("Memory", f"{self.system_metrics.memory_percent:.1f}%", mem_status)
        
        # Disk
        disk_status = "🔴 HIGH" if self.system_metrics.disk_percent > self.alert_threshold['disk'] else "🟢 OK"
        table.add_row("Disk Usage", f"{self.system_metrics.disk_percent:.1f}%", disk_status)
        
        # Load Average
        load_1, load_5, load_15 = self.system_metrics.load_average
        table.add_row("Load Avg", f"{load_1:.2f}, {load_5:.2f}, {load_15:.2f}", "🟢 OK")
        
        # Network
        net_in_mb = self.system_metrics.network_in / (1024 * 1024)
        net_out_mb = self.system_metrics.network_out / (1024 * 1024)
        table.add_row("Network I/O", f"↓{net_in_mb:.1f}MB ↑{net_out_mb:.1f}MB", "🟢 OK")
        
        return Panel(table, title="🖥️  System Metrics", border_style="blue")
    
    def create_security_panel(self) -> Panel:
        """Create security metrics panel"""
        table = Table(show_header=True, header_style="bold red", box=box.ROUNDED)
        table.add_column("Security Metric", style="cyan", width=18)
        table.add_column("Value", style="white", width=15)
        table.add_column("Threat Level", style="yellow", width=12)
        
        # Failed logins
        login_threat = "🔴 HIGH" if self.security_metrics.failed_logins > self.alert_threshold['failed_logins'] else "🟢 LOW"
        table.add_row("Failed Logins", str(self.security_metrics.failed_logins), login_threat)
        
        # Suspicious IPs
        ip_count = len(self.security_metrics.suspicious_ips)
        ip_threat = "🟡 MEDIUM" if ip_count > 5 else "🟢 LOW"
        table.add_row("Suspicious IPs", str(ip_count), ip_threat)
        
        # SSL Certificate
        ssl_threat = "🔴 CRITICAL" if self.security_metrics.ssl_certificate_days < 7 else "🟢 OK"
        table.add_row("SSL Cert Days", str(self.security_metrics.ssl_certificate_days), ssl_threat)
        
        # Rate Limiting
        rate_threat = "🟡 MEDIUM" if self.security_metrics.rate_limit_hits > 100 else "🟢 LOW"
        table.add_row("Rate Limit Hits", str(self.security_metrics.rate_limit_hits), rate_threat)
        
        # Active Connections
        table.add_row("Active Connections", str(self.security_metrics.active_connections), "🟢 NORMAL")
        
        return Panel(table, title="🛡️  Security Metrics", border_style="red")
    
    def create_service_panel(self) -> Panel:
        """Create service status panel"""
        table = Table(show_header=True, header_style="bold green", box=box.ROUNDED)
        table.add_column("Service", style="cyan", width=15)
        table.add_column("Status", style="white", width=12)
        table.add_column("Response Time", style="yellow", width=15)
        
        services = {
            "Nginx": self.service_metrics.nginx_status,
            "Landing Page": self.service_metrics.landing_page_status,
            "Backend API": self.service_metrics.backend_api_status,
            "Certbot": self.service_metrics.certbot_status
        }
        
        for service, status in services.items():
            status_icon = "🟢" if status == "healthy" else "🔴" if status == "unhealthy" else "🟡"
            response_time = self.service_metrics.response_times.get(service.lower().replace(' ', '_'), 0)
            rt_display = f"{response_time*1000:.0f}ms" if response_time < 10 else "TIMEOUT"
            table.add_row(service, f"{status_icon} {status.upper()}", rt_display)
        
        return Panel(table, title="🚀 Service Status", border_style="green")
    
    def create_alerts_panel(self) -> Panel:
        """Create alerts and notifications panel"""
        alerts = []
        
        # System alerts
        if self.system_metrics.cpu_percent > self.alert_threshold['cpu']:
            alerts.append("🔴 HIGH CPU USAGE DETECTED")
        if self.system_metrics.memory_percent > self.alert_threshold['memory']:
            alerts.append("🔴 HIGH MEMORY USAGE DETECTED")
        if self.system_metrics.disk_percent > self.alert_threshold['disk']:
            alerts.append("🔴 HIGH DISK USAGE DETECTED")
        
        # Security alerts
        if self.security_metrics.failed_logins > self.alert_threshold['failed_logins']:
            alerts.append("🛡️ MULTIPLE FAILED LOGIN ATTEMPTS")
        if len(self.security_metrics.suspicious_ips) > 5:
            alerts.append("🛡️ SUSPICIOUS IP ACTIVITY DETECTED")
        if self.security_metrics.ssl_certificate_days < 7:
            alerts.append("🔒 SSL CERTIFICATE EXPIRING SOON")
        
        # Service alerts
        for service, rt in self.service_metrics.response_times.items():
            if rt > self.alert_threshold['response_time']:
                alerts.append(f"⚡ HIGH RESPONSE TIME: {service.upper()}")
        
        if not alerts:
            alerts.append("🟢 ALL SYSTEMS OPERATIONAL")
        
        alert_text = "\n".join(alerts)
        return Panel(alert_text, title="🚨 Active Alerts", border_style="red")
    
    def create_dashboard_layout(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        # Header
        header = Panel(
            Align.center(
                Text("🛡️ ArtifactVirtual Security Monitor Dashboard 🛡️", style="bold white on blue"),
                vertical="middle"
            ),
            title=f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="blue"
        )
        
        # Create main sections
        layout.split_column(
            Layout(header, size=3),
            Layout(name="main", ratio=1)
        )
        
        # Split main area
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Split left column
        layout["left"].split_column(
            Layout(self.create_system_panel()),
            Layout(self.create_security_panel())
        )
        
        # Split right column  
        layout["right"].split_column(
            Layout(self.create_service_panel()),
            Layout(self.create_alerts_panel())
        )
        
        return layout
    
    async def run_dashboard(self):
        """Run the monitoring dashboard"""
        self.console.print("[bold green]🚀 Starting ArtifactVirtual Security Monitor...[/bold green]")
        
        with Live(self.create_dashboard_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                try:
                    # Collect all metrics
                    await asyncio.gather(
                        self.collect_system_metrics(),
                        self.collect_security_metrics(),
                        self.collect_service_metrics()
                    )
                    
                    # Update dashboard
                    live.update(self.create_dashboard_layout())
                    
                    # Wait before next update
                    await asyncio.sleep(5)
                    
                except KeyboardInterrupt:
                    self.console.print("[yellow]Dashboard stopped by user[/yellow]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Dashboard error: {e}[/red]")
                    await asyncio.sleep(2)


async def main():
    monitor = SecurityMonitor()
    await monitor.run_dashboard()


if __name__ == "__main__":
    asyncio.run(main())
