#!/usr/bin/env python3
"""
Unified Security Dashboard Launcher
Launch multiple monitoring dashboards simultaneously
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text


class DashboardLauncher:
    def __init__(self):
        self.console = Console()
        self.dashboards = []
    
    def show_menu(self):
        """Show dashboard selection menu"""
        self.console.clear()
        
        title = Panel(
            Text("🛡️ ArtifactVirtual Security Dashboard Suite 🛡️", 
                 style="bold white on blue", justify="center"),
            border_style="blue"
        )
        
        options = [
            Panel("1️⃣  Security Monitor\n• System metrics\n• Security alerts\n• Service status", 
                  title="Main Dashboard", border_style="green"),
            Panel("2️⃣  Network Analyzer\n• Traffic analysis\n• Threat detection\n• Connection monitoring", 
                  title="Network Monitor", border_style="cyan"),
            Panel("3️⃣  Combined View\n• All dashboards\n• Split screen\n• Real-time sync", 
                  title="Unified Dashboard", border_style="magenta"),
            Panel("4️⃣  Exit", title="Quit", border_style="red")
        ]
        
        self.console.print(title)
        self.console.print(Columns(options, equal=True, expand=True))
        
        choice = self.console.input("\n[bold yellow]Select dashboard (1-4): [/bold yellow]")
        return choice
    
    async def launch_security_monitor(self):
        """Launch security monitoring dashboard"""
        self.console.print("[green]🚀 Launching Security Monitor...[/green]")
        try:
            from security_monitor import SecurityMonitor
            monitor = SecurityMonitor()
            await monitor.run_dashboard()
        except ImportError:
            self.console.print("[red]❌ Security monitor not found[/red]")
    
    async def launch_network_analyzer(self):
        """Launch network analysis dashboard"""
        self.console.print("[cyan]🚀 Launching Network Analyzer...[/cyan]")
        try:
            from network_analyzer import NetworkAnalyzer
            analyzer = NetworkAnalyzer()
            await analyzer.run_analyzer()
        except ImportError:
            self.console.print("[red]❌ Network analyzer not found[/red]")
    
    async def launch_combined_dashboard(self):
        """Launch combined dashboard view"""
        self.console.print("[magenta]🚀 Launching Combined Dashboard...[/magenta]")
        
        # Create tasks for both dashboards
        tasks = [
            asyncio.create_task(self.launch_security_monitor()),
            asyncio.create_task(self.launch_network_analyzer())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.console.print("[yellow]Dashboard suite stopped[/yellow]")
    
    async def run(self):
        """Main launcher loop"""
        while True:
            try:
                choice = self.show_menu()
                
                if choice == "1":
                    await self.launch_security_monitor()
                elif choice == "2":
                    await self.launch_network_analyzer()
                elif choice == "3":
                    await self.launch_combined_dashboard()
                elif choice == "4":
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                else:
                    self.console.print("[red]❌ Invalid choice[/red]")
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                self.console.print("[yellow]\n👋 Exiting dashboard suite...[/yellow]")
                break


async def main():
    launcher = DashboardLauncher()
    await launcher.run()


if __name__ == "__main__":
    asyncio.run(main())
