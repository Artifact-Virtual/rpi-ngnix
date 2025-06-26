# Reverse Ingress-Nginx Infrastructure - AI Automation Suite PowerShell Launcher
# Advanced AI-powered automation with Puppeteer and monitoring

param(
    [Parameter(Position=0)]
    [ValidateSet("dashboard", "health", "security", "performance", "content", "visual", "all", "report", "install", "help")]
    [string]$Command = "help",
    
    [switch]$Headless,
    [switch]$Verbose,
    [string]$ConfigPath = "automation_config\config.json"
)

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️ $Message" -ForegroundColor Yellow }

# Main header
function Show-Header {
    Clear-Host
    Write-Host @"
🤖 AI Automation Suite - PowerShell Launcher
============================================
Advanced Puppeteer-based AI automation for web testing,
monitoring, security scanning, and performance analysis.

"@ -ForegroundColor Blue
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-Success "Node.js found: $nodeVersion"
        } else {
            throw "Node.js not found"
        }
    } catch {
        Write-Error "Node.js is not installed or not in PATH"
        Write-Info "Please install Node.js from https://nodejs.org/"
        return $false
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        if ($npmVersion) {
            Write-Success "npm found: v$npmVersion"
        }
    } catch {
        Write-Warning "npm not found, but continuing..."
    }
    
    # Check Python (optional)
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Success "Python found: $pythonVersion"
        }
    } catch {
        Write-Warning "Python not found (optional for advanced features)"
    }
    
    # Check if in correct directory
    if (-not (Test-Path "automation_scripts")) {
        Write-Error "automation_scripts directory not found"
        Write-Info "Please run this script from the cert-nginx directory"
        return $false
    }
    
    Write-Success "Prerequisites check completed"
    return $true
}

# Install dependencies
function Install-Dependencies {
    Write-Info "Installing Node.js dependencies..."
    
    if (-not (Test-Path "node_modules")) {
        try {
            npm install
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Dependencies installed successfully"
            } else {
                Write-Error "Failed to install dependencies"
                return $false
            }
        } catch {
            Write-Error "Error installing dependencies: $_"
            return $false
        }
    } else {
        Write-Info "Dependencies already installed"
    }
    
    return $true
}

# Start AI Dashboard
function Start-Dashboard {
    Write-Info "Starting AI Automation Dashboard..."
    Write-Info "Dashboard will be available at: automation_logs/dashboard.html"
    Write-Info "WebSocket server will run on port 8444"
    Write-Warning "Press Ctrl+C to stop the dashboard"
    
    try {
        if ($Headless) {
            # Update config for headless mode
            Update-Config -Headless $true
        }
        
        node "automation_scripts\orchestrator_fixed.js" dashboard
    } catch {
        Write-Error "Failed to start dashboard: $_"
    }
}

# Run specific automation task
function Invoke-AutomationTask {
    param([string]$TaskType)
    
    Write-Info "Running $TaskType automation task..."
    
    try {
        $scriptPath = switch ($TaskType) {
            "health" { "automation_scripts\automation.js" }
            default { "automation_scripts\advanced_ai_automation.js" }
        }
        
        node $scriptPath $TaskType
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$TaskType task completed successfully"
        } else {
            Write-Error "$TaskType task failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-Error "Error running $TaskType task: $_"
    }
}

# Generate comprehensive report
function New-Report {
    Write-Info "Generating comprehensive automation report..."
    
    try {
        node "automation_scripts\orchestrator_fixed.js" report
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Report generated successfully"
            Write-Info "Check automation_logs/reports/ for the generated report"
        } else {
            Write-Error "Report generation failed"
        }
    } catch {
        Write-Error "Error generating report: $_"
    }
}

# Update configuration
function Update-Config {
    param([bool]$Headless = $false)
    
    if (Test-Path $ConfigPath) {
        try {
            $config = Get-Content $ConfigPath | ConvertFrom-Json
            $config.headless = $Headless
            $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath
            Write-Success "Configuration updated"
        } catch {
            Write-Warning "Could not update configuration: $_"
        }
    }
}

# Show interactive menu
function Show-Menu {
    do {
        Write-Host @"

📋 Available Commands:
┌─────────────────────────────────────────────┐
│ 1. dashboard    - Start AI Dashboard        │
│ 2. health       - Run Health Check          │
│ 3. security     - Run Security Scan         │
│ 4. performance  - Run Performance Test      │
│ 5. content      - Run Content Analysis      │
│ 6. visual       - Run Visual Regression     │
│ 7. all          - Run Complete Suite        │
│ 8. report       - Generate Report           │
│ 9. install      - Install Dependencies      │
│ 0. exit         - Exit                      │
└─────────────────────────────────────────────┘

"@ -ForegroundColor White
        
        $choice = Read-Host "Enter your choice (0-9)"
        
        switch ($choice) {
            "1" { Start-Dashboard; break }
            "2" { Invoke-AutomationTask "health"; break }
            "3" { Invoke-AutomationTask "security"; break }
            "4" { Invoke-AutomationTask "performance"; break }
            "5" { Invoke-AutomationTask "content"; break }
            "6" { Invoke-AutomationTask "visual"; break }
            "7" { Invoke-AutomationTask "all"; break }
            "8" { New-Report; break }
            "9" { Install-Dependencies; break }
            "0" { Write-Info "Goodbye!"; return }
            default { Write-Warning "Invalid choice. Please select 0-9." }
        }
        
        if ($choice -ne "0") {
            Read-Host "Press Enter to continue..."
        }
    } while ($choice -ne "0")
}

# Show help
function Show-Help {
    Write-Host @"
🤖 AI Automation Suite - PowerShell Launcher

USAGE:
    .\start_ai_automation.ps1 [COMMAND] [OPTIONS]

COMMANDS:
    dashboard     Start AI Automation Dashboard (recommended)
    health        Run health check automation
    security      Run security scan with vulnerability detection
    performance   Run performance testing with Core Web Vitals
    content       Run AI-powered content analysis
    visual        Run visual regression testing
    all           Run complete automation suite
    report        Generate comprehensive report
    install       Install Node.js dependencies
    help          Show this help message

OPTIONS:
    -Headless     Run browser in headless mode
    -Verbose      Enable verbose logging
    -ConfigPath   Specify custom config file path

EXAMPLES:
    .\start_ai_automation.ps1 dashboard
    .\start_ai_automation.ps1 security -Headless
    .\start_ai_automation.ps1 all -Verbose
    .\start_ai_automation.ps1 report

FEATURES:
    🏥 Health Monitoring      - Continuous site health checks
    🛡️ Security Scanning      - Advanced vulnerability detection
    ⚡ Performance Testing    - Core Web Vitals measurement
    🧠 Content Analysis       - AI-powered SEO and content quality
    📸 Visual Regression      - Automated visual testing
    📊 Real-time Dashboard    - WebSocket-powered monitoring
    🤖 AI Orchestration      - Intelligent task management

REQUIREMENTS:
    - Node.js 18+ (https://nodejs.org/)
    - Chrome/Chromium browser
    - PowerShell 5.1 or PowerShell Core

"@ -ForegroundColor White
}

# Main execution
Show-Header

if (-not (Test-Prerequisites)) {
    Write-Error "Prerequisites check failed. Please resolve the issues above."
    exit 1
}

switch ($Command.ToLower()) {
    "dashboard" {
        if (-not (Install-Dependencies)) { exit 1 }
        Start-Dashboard
    }
    "health" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "health"
    }
    "security" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "security"
    }
    "performance" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "performance"  
    }
    "content" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "content"
    }
    "visual" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "visual"
    }
    "all" {
        if (-not (Install-Dependencies)) { exit 1 }
        Invoke-AutomationTask "all"
    }
    "report" {
        New-Report
    }
    "install" {
        Install-Dependencies
    }
    "help" {
        Show-Help
    }
    default {
        Show-Menu
    }
}

Write-Host "`n🎉 AI Automation Suite execution completed!" -ForegroundColor Green
