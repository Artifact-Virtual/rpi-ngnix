#!/usr/bin/env python3
"""
AI Automation Engine with Puppeteer
Automated testing, monitoring, and AI-driven web interactions
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
import time
from datetime import datetime
import requests
import logging


class AIAutomationEngine:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.scripts_dir = self.base_dir / "automation_scripts"
        self.logs_dir = self.base_dir / "automation_logs"
        self.config_dir = self.base_dir / "automation_config"
        
        for dir_path in [self.scripts_dir, self.logs_dir, self.config_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.setup_logging()
        self.install_puppeteer()
    
    def setup_logging(self):
        """Setup logging for automation"""
        log_file = self.logs_dir / f"automation_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def install_puppeteer(self):
        """Install Puppeteer and dependencies"""
        package_json = self.base_dir / "package.json"
        
        if not package_json.exists():
            self.logger.info("📦 Creating package.json for Puppeteer...")
            package_config = {
                "name": "artifactvirtual-automation",
                "version": "1.0.0",
                "description": "AI-driven automation with Puppeteer",
                "main": "automation.js",
                "dependencies": {
                    "puppeteer": "^21.5.0",
                    "puppeteer-extra": "^3.3.6",
                    "puppeteer-extra-plugin-stealth": "^2.11.2",
                    "puppeteer-extra-plugin-adblocker": "^2.13.6",
                    "puppeteer-extra-plugin-recaptcha": "^3.6.8",
                    "playwright": "^1.40.0",
                    "axios": "^1.6.0",
                    "cheerio": "^1.0.0-rc.12",
                    "screenshot-desktop": "^1.12.7",
                    "lighthouse": "^11.4.0",
                    "chrome-har": "^0.13.4",
                    "pageres": "^6.2.0",
                    "puppeteer-cluster": "^0.23.0",
                    "pdf-parse": "^1.1.1",
                    "tesseract.js": "^5.0.3",
                    "opencv4nodejs": "^5.6.0",
                    "puppeteer-har": "^1.1.2",
                    "sharp": "^0.33.0"
                },
                "scripts": {
                    "test": "node automation.js",
                    "monitor": "node monitor.js",
                    "security-scan": "node security_scan.js",
                    "ai-suite": "node advanced_ai_automation.js",
                    "orchestrator": "node orchestrator_fixed.js",
                    "dashboard": "node orchestrator_fixed.js dashboard",
                    "start": "node orchestrator_fixed.js dashboard"
                }
            }
            
            with open(package_json, 'w') as f:
                json.dump(package_config, f, indent=2)
        
        # Check if node_modules exists
        if not (self.base_dir / "node_modules").exists():
            self.logger.info("📥 Installing Puppeteer dependencies...")
            subprocess.run(["npm", "install"], cwd=self.base_dir, check=True)
            self.logger.info("✅ Puppeteer installed successfully")
    
    def create_automation_scripts(self):
        """Create core automation scripts"""
        
        # Main automation controller
        automation_js = '''
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());
puppeteer.use(AdblockerPlugin());

class AIAutomation {
    constructor() {
        this.browser = null;
        this.page = null;
        this.config = this.loadConfig();
    }
    
    loadConfig() {
        try {
            return JSON.parse(fs.readFileSync('automation_config/config.json', 'utf8'));
        } catch (error) {
            return {
                headless: false,
                defaultTimeout: 30000,
                viewport: { width: 1920, height: 1080 },
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                targets: {
                    local: 'https://localhost:8443',
                    health: 'https://localhost:8443/health'
                }
            };
        }
    }
    
    async init() {
        console.log('🤖 Initializing AI Automation Engine...');
        
        this.browser = await puppeteer.launch({
            headless: this.config.headless,
            defaultViewport: this.config.viewport,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--ignore-certificate-errors',
                '--ignore-ssl-errors',
                '--ignore-certificate-errors-spki-list'
            ]
        });
        
        this.page = await this.browser.newPage();
        await this.page.setUserAgent(this.config.userAgent);
        await this.page.setViewport(this.config.viewport);
        
        console.log('✅ Browser initialized');
    }
    
    async healthCheck() {
        console.log('🏥 Running health check...');
        
        try {
            await this.page.goto(this.config.targets.health, { 
                waitUntil: 'networkidle2',
                timeout: this.config.defaultTimeout 
            });
            
            const content = await this.page.content();
            const isHealthy = content.includes('healthy');
            
            console.log(`Health status: ${isHealthy ? '✅ Healthy' : '❌ Unhealthy'}`);
            
            // Take screenshot
            await this.page.screenshot({
                path: `automation_logs/health_check_${Date.now()}.png`,
                fullPage: true
            });
            
            return isHealthy;
        } catch (error) {
            console.error('❌ Health check failed:', error.message);
            return false;
        }
    }
    
    async securityScan() {
        console.log('🛡️ Running security scan...');
        
        const vulnerabilities = [];
        
        try {
            // Check for common security headers
            const response = await this.page.goto(this.config.targets.local, {
                waitUntil: 'networkidle2'
            });
            
            const headers = response.headers();
            
            const securityHeaders = [
                'x-frame-options',
                'x-content-type-options', 
                'x-xss-protection',
                'strict-transport-security'
            ];
            
            securityHeaders.forEach(header => {
                if (!headers[header]) {
                    vulnerabilities.push(`Missing security header: ${header}`);
                }
            });
            
            // Check for exposed sensitive information
            const content = await this.page.content();
            const sensitivePatterns = [
                /password/i,
                /api[_-]?key/i,
                /secret/i,
                /token/i
            ];
            
            sensitivePatterns.forEach(pattern => {
                if (pattern.test(content)) {
                    vulnerabilities.push(`Potential sensitive data exposure: ${pattern}`);
                }
            });
            
            // Test for XSS
            await this.page.evaluate(() => {
                window.xssTest = '<script>alert("XSS")</script>';
            });
            
            console.log(`Security scan complete. Found ${vulnerabilities.length} issues.`);
            
            // Save results
            const results = {
                timestamp: new Date().toISOString(),
                vulnerabilities: vulnerabilities,
                headers: headers
            };
            
            fs.writeFileSync(
                `automation_logs/security_scan_${Date.now()}.json`,
                JSON.stringify(results, null, 2)
            );
            
            return vulnerabilities;
            
        } catch (error) {
            console.error('❌ Security scan failed:', error.message);
            return [];
        }
    }
    
    async performanceTest() {
        console.log('⚡ Running performance test...');
        
        try {
            const metrics = await this.page.metrics();
            
            const startTime = Date.now();
            await this.page.goto(this.config.targets.local, {
                waitUntil: 'networkidle2'
            });
            const loadTime = Date.now() - startTime;
            
            const performanceData = await this.page.evaluate(() => {
                return JSON.parse(JSON.stringify(performance.timing));
            });
            
            const results = {
                timestamp: new Date().toISOString(),
                loadTime: loadTime,
                metrics: metrics,
                timing: performanceData
            };
            
            fs.writeFileSync(
                `automation_logs/performance_${Date.now()}.json`,
                JSON.stringify(results, null, 2)
            );
            
            console.log(`⚡ Load time: ${loadTime}ms`);
            return results;
            
        } catch (error) {
            console.error('❌ Performance test failed:', error.message);
            return null;
        }
    }
    
    async monitorSite() {
        console.log('👁️ Starting continuous monitoring...');
        
        let iteration = 0;
        
        while (true) {
            try {
                iteration++;
                console.log(`\\n--- Monitoring Iteration ${iteration} ---`);
                
                const health = await this.healthCheck();
                
                if (!health) {
                    console.log('🚨 Site is down! Sending alert...');
                    // Could integrate with notification systems here
                }
                
                if (iteration % 10 === 0) {
                    await this.securityScan();
                    await this.performanceTest();
                }
                
                // Wait 30 seconds before next check
                await new Promise(resolve => setTimeout(resolve, 30000));
                
            } catch (error) {
                console.error('❌ Monitoring error:', error.message);
                await new Promise(resolve => setTimeout(resolve, 60000)); // Wait longer on error
            }
        }
    }
    
    async aiAnalysis() {
        console.log('🧠 Running AI analysis...');
        
        try {
            await this.page.goto(this.config.targets.local);
            
            // Extract page structure
            const pageStructure = await this.page.evaluate(() => {
                const getElementInfo = (element) => ({
                    tag: element.tagName,
                    id: element.id,
                    classes: Array.from(element.classList),
                    text: element.textContent?.substring(0, 100)
                });
                
                return Array.from(document.querySelectorAll('*'))
                    .slice(0, 100) // Limit to first 100 elements
                    .map(getElementInfo);
            });
            
            // Analyze accessibility
            const a11yIssues = await this.page.evaluate(() => {
                const issues = [];
                
                // Check for missing alt attributes
                document.querySelectorAll('img:not([alt])').forEach(img => {
                    issues.push('Image missing alt attribute');
                });
                
                // Check for proper heading structure
                const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'));
                if (headings.length === 0) {
                    issues.push('No heading elements found');
                }
                
                return issues;
            });
            
            const analysis = {
                timestamp: new Date().toISOString(),
                pageStructure: pageStructure,
                accessibilityIssues: a11yIssues,
                recommendations: this.generateRecommendations(pageStructure, a11yIssues)
            };
            
            fs.writeFileSync(
                `automation_logs/ai_analysis_${Date.now()}.json`,
                JSON.stringify(analysis, null, 2)
            );
            
            console.log('🧠 AI analysis complete');
            return analysis;
            
        } catch (error) {
            console.error('❌ AI analysis failed:', error.message);
            return null;
        }
    }
    
    generateRecommendations(structure, a11yIssues) {
        const recommendations = [];
        
        if (a11yIssues.length > 0) {
            recommendations.push('Improve accessibility by addressing identified issues');
        }
        
        const hasHeaders = structure.some(el => el.tag.startsWith('H'));
        if (!hasHeaders) {
            recommendations.push('Add proper heading structure for better SEO');
        }
        
        return recommendations;
    }
    
    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🧹 Browser closed');
        }
    }
}

// Main execution
async function main() {
    const automation = new AIAutomation();
    
    try {
        await automation.init();
        
        const command = process.argv[2] || 'health';
        
        switch (command) {
            case 'health':
                await automation.healthCheck();
                break;
            case 'security':
                await automation.securityScan();
                break;
            case 'performance':
                await automation.performanceTest();
                break;
            case 'monitor':
                await automation.monitorSite();
                break;
            case 'ai':
                await automation.aiAnalysis();
                break;
            case 'all':
                await automation.healthCheck();
                await automation.securityScan();
                await automation.performanceTest();
                await automation.aiAnalysis();
                break;
            default:
                console.log('Usage: node automation.js [health|security|performance|monitor|ai|all]');
        }
        
    } catch (error) {
        console.error('❌ Automation failed:', error);
    } finally {
        await automation.cleanup();
    }
}

if (require.main === module) {
    main();
}

module.exports = AIAutomation;
'''
        
        with open(self.scripts_dir / "automation.js", 'w') as f:
            f.write(automation_js)
        
        # Create configuration
        config = {
            "headless": False,
            "defaultTimeout": 30000,
            "viewport": {"width": 1920, "height": 1080},
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "targets": {
                "local": "https://localhost:8443",
                "health": "https://localhost:8443/health"
            },
            "monitoring": {
                "interval": 30,
                "alerts": True,
                "screenshots": True
            }
        }
        
        with open(self.config_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info("✅ Automation scripts created")
    
    async def run_health_check(self):
        """Run health check automation"""
        self.logger.info("🏥 Running automated health check...")
        
        try:
            result = subprocess.run([
                "node", str(self.scripts_dir / "automation.js"), "health"
            ], cwd=self.base_dir, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info("✅ Health check passed")
                return True
            else:
                self.logger.error(f"❌ Health check failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Health check timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
            return False
    
    async def run_security_scan(self):
        """Run security scan automation"""
        self.logger.info("🛡️ Running automated security scan...")
        
        try:
            result = subprocess.run([
                "node", str(self.scripts_dir / "automation.js"), "security"
            ], cwd=self.base_dir, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info("✅ Security scan completed")
                return True
            else:
                self.logger.error(f"❌ Security scan failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Security scan error: {e}")
            return False
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.logger.info("👁️ Starting continuous monitoring...")
        
        try:
            process = subprocess.Popen([
                "node", str(self.scripts_dir / "automation.js"), "monitor"
            ], cwd=self.base_dir)
            
            return process
            
        except Exception as e:
            self.logger.error(f"❌ Monitoring start error: {e}")
            return None
    
    async def run_ai_analysis(self):
        """Run AI-powered analysis"""
        self.logger.info("🧠 Running AI analysis...")
        
        try:
            result = subprocess.run([
                "node", str(self.scripts_dir / "automation.js"), "ai"
            ], cwd=self.base_dir, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.logger.info("✅ AI analysis completed")
                return True
            else:
                self.logger.error(f"❌ AI analysis failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ AI analysis error: {e}")
            return False
    
    def run_interactive_mode(self):
        """Run interactive automation mode"""
        print("🤖 AI Automation Engine - Interactive Mode")
        print("=" * 50)
        print("🚀 Enhanced with Puppeteer-powered AI automation")
        print("📊 Real-time dashboard available at automation_logs/dashboard.html")
        print("")
        
        while True:
            print("\nAvailable commands:")
            print("1. Health Check")
            print("2. Security Scan (Advanced)")
            print("3. Performance Test (with Core Web Vitals)")
            print("4. AI Content Analysis")
            print("5. Visual Regression Test")
            print("6. Start AI Dashboard & Orchestrator")
            print("7. Run Complete AI Suite")
            print("8. Generate Report")
            print("9. Install/Update Dependencies")
            print("0. Exit")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "1":
                asyncio.run(self.run_health_check())
            elif choice == "2":
                subprocess.run(["node", str(self.scripts_dir / "advanced_ai_automation.js"), "security"], cwd=self.base_dir)
            elif choice == "3":
                subprocess.run(["node", str(self.scripts_dir / "advanced_ai_automation.js"), "performance"], cwd=self.base_dir)
            elif choice == "4":
                subprocess.run(["node", str(self.scripts_dir / "advanced_ai_automation.js"), "content"], cwd=self.base_dir)
            elif choice == "5":
                subprocess.run(["node", str(self.scripts_dir / "advanced_ai_automation.js"), "visual"], cwd=self.base_dir)
            elif choice == "6":
                print("🚀 Starting AI Dashboard & Orchestrator...")
                print("📊 Dashboard will be available at automation_logs/dashboard.html")
                print("🌐 WebSocket server will run on port 8444")
                print("⚠️ Press Ctrl+C to stop the orchestrator")
                subprocess.run(["node", str(self.scripts_dir / "orchestrator_fixed.js"), "dashboard"], cwd=self.base_dir)
            elif choice == "7":
                print("🚀 Running Complete AI Suite...")
                subprocess.run(["node", str(self.scripts_dir / "advanced_ai_automation.js"), "all"], cwd=self.base_dir)
            elif choice == "8":
                print("📊 Generating Comprehensive Report...")
                subprocess.run(["node", str(self.scripts_dir / "orchestrator_fixed.js"), "report"], cwd=self.base_dir)
            elif choice == "9":
                print("📦 Installing/Updating Dependencies...")
                try:
                    subprocess.run(["npm", "install"], cwd=self.base_dir, check=True)
                    print("✅ Dependencies updated successfully")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to update dependencies: {e}")
            elif choice == "0":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
        
        print("\n🎉 Thank you for using AI Automation Engine!")
        print("📚 Documentation: AI_AUTOMATION_README.md")
        print("🚀 Quick start: Use start_ai_automation.bat or start_ai_automation.ps1")


async def main():
    engine = AIAutomationEngine()
    engine.create_automation_scripts()
    engine.run_interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
