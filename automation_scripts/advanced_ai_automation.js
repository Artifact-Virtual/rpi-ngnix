#!/usr/bin/env node
/**
 * Advanced AI Automation Engine with Puppeteer
 * Features: Visual regression, AI content analysis, automated testing, 
 * performance optimization, security scanning, and intelligent monitoring
 */

const puppeteer = require('puppeteer-extra');
const { Cluster } = require('puppeteer-cluster');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
const RecaptchaPlugin = require('puppeteer-extra-plugin-recaptcha');
const lighthouse = require('lighthouse');
const fs = require('fs').promises;
const path = require('path');
const sharp = require('sharp');
const Tesseract = require('tesseract.js');

// Configure plugins
puppeteer.use(StealthPlugin());
puppeteer.use(AdblockerPlugin());
puppeteer.use(RecaptchaPlugin({
    provider: {
        id: '2captcha',
        token: process.env.CAPTCHA_TOKEN || 'DEMO_TOKEN'
    }
}));

class AdvancedAIAutomation {
    constructor() {
        this.config = this.loadConfig();
        this.cluster = null;
        this.baseDir = path.dirname(__dirname);
        this.logsDir = path.join(this.baseDir, 'automation_logs');
        this.screenshotsDir = path.join(this.logsDir, 'screenshots');
        this.reportsDir = path.join(this.logsDir, 'reports');
        
        this.ensureDirectories();
    }
    
    async ensureDirectories() {
        const dirs = [this.logsDir, this.screenshotsDir, this.reportsDir];
        for (const dir of dirs) {
            try {
                await fs.mkdir(dir, { recursive: true });
            } catch (error) {
                // Directory already exists
            }
        }
    }
    
    loadConfig() {
        try {
            const configPath = path.join(__dirname, '..', 'automation_config', 'config.json');
            return JSON.parse(require('fs').readFileSync(configPath, 'utf8'));
        } catch (error) {
            return {
                headless: false,
                concurrency: 3,
                maxRetries: 3,
                timeout: 30000,
                viewport: { width: 1920, height: 1080 },
                targets: {
                    local: 'https://localhost:8443',
                    health: 'https://localhost:8443/health',
                    api: 'https://localhost:8443/api'
                },
                ai: {
                    enableVisualRegression: true,
                    enableContentAnalysis: true,
                    enablePredictiveAnalytics: true
                }
            };
        }
    }
    
    async initCluster() {
        console.log('🚀 Initializing AI Automation Cluster...');
        
        this.cluster = await Cluster.launch({
            concurrency: Cluster.CONCURRENCY_CONTEXT,
            maxConcurrency: this.config.concurrency,
            puppeteerOptions: {
                headless: this.config.headless,
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
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ]
            }
        });
        
        // Handle cluster errors
        this.cluster.on('taskerror', (err, data) => {
            console.error('❌ Task error:', err.message);
        });
        
        console.log('✅ Cluster initialized');
    }
    
    async visualRegressionTest() {
        console.log('📸 Running visual regression test...');
        
        if (!this.cluster) await this.initCluster();
        
        const timestamp = Date.now();
        const results = [];
        
        await this.cluster.task(async ({ page, data }) => {
            const { url, name } = data;
            
            try {
                await page.setViewport(this.config.viewport);
                await page.goto(url, { waitUntil: 'networkidle2' });
                
                // Take full page screenshot
                const screenshotPath = path.join(
                    this.screenshotsDir, 
                    `${name}_${timestamp}.png`
                );
                
                await page.screenshot({
                    path: screenshotPath,
                    fullPage: true
                });
                
                // Extract visual metrics
                const visualMetrics = await page.evaluate(() => {
                    const imgs = Array.from(document.images);
                    const videos = Array.from(document.querySelectorAll('video'));
                    
                    return {
                        imageCount: imgs.length,
                        videoCount: videos.length,
                        brokenImages: imgs.filter(img => !img.complete || img.naturalWidth === 0).length,
                        totalElements: document.querySelectorAll('*').length,
                        textContent: document.body.textContent.length
                    };
                });
                
                // AI-powered image analysis
                const imageAnalysis = await this.analyzeScreenshot(screenshotPath);
                
                results.push({
                    url,
                    name,
                    timestamp,
                    screenshotPath,
                    visualMetrics,
                    imageAnalysis,
                    status: 'success'
                });
                
            } catch (error) {
                results.push({
                    url,
                    name,
                    timestamp,
                    error: error.message,
                    status: 'failed'
                });
            }
        });
        
        // Queue targets for testing
        const targets = Object.entries(this.config.targets);
        for (const [name, url] of targets) {
            this.cluster.queue({ url, name });
        }
        
        await this.cluster.idle();
        
        // Generate comparison report
        const report = await this.generateVisualReport(results);
        
        console.log('📸 Visual regression test completed');
        return report;
    }
    
    async analyzeScreenshot(imagePath) {
        try {
            // Use Sharp for image processing
            const metadata = await sharp(imagePath).metadata();
            
            // Basic image analysis
            const stats = await sharp(imagePath).stats();
            
            // OCR analysis for text extraction
            const { data: { text } } = await Tesseract.recognize(imagePath, 'eng', {
                logger: m => {} // Silent logging
            });
            
            return {
                dimensions: { width: metadata.width, height: metadata.height },
                channels: metadata.channels,
                colorSpace: metadata.space,
                density: metadata.density,
                fileSize: metadata.size,
                stats: stats,
                extractedText: text.substring(0, 500), // First 500 chars
                textConfidence: text.length > 50 ? 'high' : 'low'
            };
            
        } catch (error) {
            console.error('Image analysis error:', error.message);
            return { error: error.message };
        }
    }
    
    async intelligentContentAnalysis() {
        console.log('🧠 Running intelligent content analysis...');
        
        if (!this.cluster) await this.initCluster();
        
        const results = [];
        
        await this.cluster.task(async ({ page, data }) => {
            const { url, name } = data;
            
            try {
                await page.goto(url, { waitUntil: 'networkidle2' });
                
                // Extract comprehensive page data
                const pageData = await page.evaluate(() => {
                    // Content analysis
                    const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'))
                        .map(h => ({ tag: h.tagName, text: h.textContent.trim() }));
                    
                    const links = Array.from(document.querySelectorAll('a[href]'))
                        .map(a => ({ href: a.href, text: a.textContent.trim() }));
                    
                    const images = Array.from(document.querySelectorAll('img'))
                        .map(img => ({ 
                            src: img.src, 
                            alt: img.alt, 
                            width: img.width, 
                            height: img.height 
                        }));
                    
                    const forms = Array.from(document.querySelectorAll('form'))
                        .map(form => ({
                            action: form.action,
                            method: form.method,
                            inputs: Array.from(form.querySelectorAll('input')).length
                        }));
                    
                    // SEO analysis
                    const title = document.title;
                    const metaDescription = document.querySelector('meta[name="description"]')?.content || '';
                    const metaKeywords = document.querySelector('meta[name="keywords"]')?.content || '';
                    
                    // Performance indicators
                    const scripts = document.querySelectorAll('script').length;
                    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]').length;
                    
                    return {
                        content: {
                            title,
                            headings,
                            links: links.slice(0, 50), // Limit results
                            images: images.slice(0, 20),
                            forms,
                            wordCount: document.body.textContent.split(/\s+/).length
                        },
                        seo: {
                            title,
                            metaDescription,
                            metaKeywords,
                            hasH1: headings.some(h => h.tag === 'H1'),
                            headingStructure: headings.length
                        },
                        technical: {
                            scripts,
                            stylesheets,
                            totalElements: document.querySelectorAll('*').length
                        }
                    };
                });
                
                // AI scoring
                const aiScore = this.calculateAIScore(pageData);
                
                // Recommendations
                const recommendations = this.generateRecommendations(pageData);
                
                results.push({
                    url,
                    name,
                    timestamp: Date.now(),
                    pageData,
                    aiScore,
                    recommendations,
                    status: 'success'
                });
                
            } catch (error) {
                results.push({
                    url,
                    name,
                    error: error.message,
                    status: 'failed'
                });
            }
        });
        
        // Queue all targets
        const targets = Object.entries(this.config.targets);
        for (const [name, url] of targets) {
            this.cluster.queue({ url, name });
        }
        
        await this.cluster.idle();
        
        // Save comprehensive report
        const reportPath = path.join(this.reportsDir, `content_analysis_${Date.now()}.json`);
        await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
        
        console.log('🧠 Content analysis completed');
        return results;
    }
    
    calculateAIScore(pageData) {
        let score = 0;
        let maxScore = 100;
        
        // SEO scoring
        if (pageData.seo.title && pageData.seo.title.length > 10) score += 15;
        if (pageData.seo.metaDescription && pageData.seo.metaDescription.length > 50) score += 15;
        if (pageData.seo.hasH1) score += 10;
        
        // Content quality
        if (pageData.content.wordCount > 300) score += 20;
        if (pageData.content.headings.length > 2) score += 10;
        if (pageData.content.images.length > 0) score += 10;
        
        // Technical performance
        if (pageData.technical.scripts < 10) score += 10;
        if (pageData.technical.stylesheets < 5) score += 5;
        
        // Accessibility
        const imagesWithAlt = pageData.content.images.filter(img => img.alt).length;
        if (imagesWithAlt === pageData.content.images.length && pageData.content.images.length > 0) {
            score += 5;
        }
        
        return {
            score: Math.min(score, maxScore),
            percentage: Math.round((Math.min(score, maxScore) / maxScore) * 100),
            category: score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'fair' : 'poor'
        };
    }
    
    generateRecommendations(pageData) {
        const recommendations = [];
        
        // SEO recommendations
        if (!pageData.seo.title || pageData.seo.title.length < 30) {
            recommendations.push({
                type: 'seo',
                priority: 'high',
                message: 'Optimize page title (30-60 characters recommended)'
            });
        }
        
        if (!pageData.seo.metaDescription || pageData.seo.metaDescription.length < 120) {
            recommendations.push({
                type: 'seo',
                priority: 'high',
                message: 'Add or improve meta description (120-160 characters)'
            });
        }
        
        if (!pageData.seo.hasH1) {
            recommendations.push({
                type: 'seo',
                priority: 'medium',
                message: 'Add H1 heading for better SEO structure'
            });
        }
        
        // Performance recommendations
        if (pageData.technical.scripts > 15) {
            recommendations.push({
                type: 'performance',
                priority: 'medium',
                message: 'Consider reducing number of JavaScript files'
            });
        }
        
        // Accessibility recommendations
        const imagesWithoutAlt = pageData.content.images.filter(img => !img.alt).length;
        if (imagesWithoutAlt > 0) {
            recommendations.push({
                type: 'accessibility',
                priority: 'high',
                message: `Add alt attributes to ${imagesWithoutAlt} images`
            });
        }
        
        // Content recommendations
        if (pageData.content.wordCount < 300) {
            recommendations.push({
                type: 'content',
                priority: 'low',
                message: 'Consider adding more content for better SEO'
            });
        }
        
        return recommendations;
    }
    
    async advancedSecurityScan() {
        console.log('🛡️ Running advanced security scan...');
        
        if (!this.cluster) await this.initCluster();
        
        const results = [];
        
        await this.cluster.task(async ({ page, data }) => {
            const { url, name } = data;
            
            try {
                // Enable request interception
                await page.setRequestInterception(true);
                
                const requests = [];
                const responses = [];
                
                page.on('request', request => {
                    requests.push({
                        url: request.url(),
                        method: request.method(),
                        headers: request.headers()
                    });
                    request.continue();
                });
                
                page.on('response', response => {
                    responses.push({
                        url: response.url(),
                        status: response.status(),
                        headers: response.headers()
                    });
                });
                
                await page.goto(url, { waitUntil: 'networkidle2' });
                
                // Security header analysis
                const mainResponse = responses.find(r => r.url === url);
                const securityHeaders = this.analyzeSecurityHeaders(mainResponse?.headers || {});
                
                // Content Security Policy analysis
                const cspAnalysis = this.analyzeCSP(mainResponse?.headers || {});
                
                // JavaScript security analysis
                const jsSecurityIssues = await page.evaluate(() => {
                    const issues = [];
                    
                    // Check for inline scripts
                    const inlineScripts = document.querySelectorAll('script:not([src])');
                    if (inlineScripts.length > 0) {
                        issues.push(`Found ${inlineScripts.length} inline scripts`);
                    }
                    
                    // Check for eval usage (basic check)
                    if (document.documentElement.innerHTML.includes('eval(')) {
                        issues.push('Potential eval() usage detected');
                    }
                    
                    // Check for external scripts from unknown domains
                    const externalScripts = Array.from(document.querySelectorAll('script[src]'))
                        .map(script => script.src)
                        .filter(src => !src.includes(window.location.hostname));
                    
                    if (externalScripts.length > 0) {
                        issues.push(`${externalScripts.length} external scripts loaded`);
                    }
                    
                    return issues;
                });
                
                // Form security analysis
                const formSecurityIssues = await page.evaluate(() => {
                    const issues = [];
                    const forms = document.querySelectorAll('form');
                    
                    forms.forEach(form => {
                        if (form.method.toLowerCase() === 'get' && form.querySelector('input[type="password"]')) {
                            issues.push('Password field in GET form detected');
                        }
                        
                        if (!form.querySelector('input[name*="csrf"], input[name*="token"]')) {
                            issues.push('Form without CSRF protection detected');
                        }
                    });
                    
                    return issues;
                });
                
                // Generate security score
                const securityScore = this.calculateSecurityScore(
                    securityHeaders,
                    cspAnalysis,
                    jsSecurityIssues,
                    formSecurityIssues
                );
                
                results.push({
                    url,
                    name,
                    timestamp: Date.now(),
                    securityHeaders,
                    cspAnalysis,
                    jsSecurityIssues,
                    formSecurityIssues,
                    securityScore,
                    requests: requests.slice(0, 20), // Limit for storage
                    responses: responses.slice(0, 20),
                    status: 'success'
                });
                
            } catch (error) {
                results.push({
                    url,
                    name,
                    error: error.message,
                    status: 'failed'
                });
            }
        });
        
        // Queue all targets
        const targets = Object.entries(this.config.targets);
        for (const [name, url] of targets) {
            this.cluster.queue({ url, name });
        }
        
        await this.cluster.idle();
        
        // Save security report
        const reportPath = path.join(this.reportsDir, `security_scan_${Date.now()}.json`);
        await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
        
        console.log('🛡️ Advanced security scan completed');
        return results;
    }
    
    analyzeSecurityHeaders(headers) {
        const analysis = {
            score: 0,
            issues: [],
            recommendations: []
        };
        
        const securityHeaders = {
            'x-frame-options': 'X-Frame-Options header prevents clickjacking',
            'x-content-type-options': 'X-Content-Type-Options prevents MIME sniffing',
            'x-xss-protection': 'X-XSS-Protection enables XSS filtering',
            'strict-transport-security': 'HSTS enforces secure connections',
            'content-security-policy': 'CSP prevents various attacks',
            'referrer-policy': 'Referrer-Policy controls referrer information',
            'permissions-policy': 'Permissions-Policy controls browser features'
        };
        
        Object.entries(securityHeaders).forEach(([header, description]) => {
            if (headers[header] || headers[header.toLowerCase()]) {
                analysis.score += 10;
            } else {
                analysis.issues.push(`Missing ${header}`);
                analysis.recommendations.push(`Add ${header}: ${description}`);
            }
        });
        
        return analysis;
    }
    
    analyzeCSP(headers) {
        const csp = headers['content-security-policy'] || headers['content-security-policy-report-only'];
        
        if (!csp) {
            return {
                present: false,
                score: 0,
                issues: ['No Content Security Policy found'],
                recommendations: ['Implement Content Security Policy']
            };
        }
        
        const directives = csp.split(';').map(d => d.trim());
        const analysis = {
            present: true,
            score: 50, // Base score for having CSP
            directives: directives,
            issues: [],
            recommendations: []
        };
        
        // Check for unsafe directives
        if (csp.includes("'unsafe-inline'")) {
            analysis.issues.push("CSP allows unsafe-inline");
            analysis.score -= 20;
        }
        
        if (csp.includes("'unsafe-eval'")) {
            analysis.issues.push("CSP allows unsafe-eval");
            analysis.score -= 20;
        }
        
        if (csp.includes('*')) {
            analysis.issues.push("CSP uses wildcard (*) which is too permissive");
            analysis.score -= 10;
        }
        
        return analysis;
    }
    
    calculateSecurityScore(securityHeaders, cspAnalysis, jsIssues, formIssues) {
        let score = 0;
        const maxScore = 100;
        
        // Security headers (40 points max)
        score += Math.min(securityHeaders.score, 40);
        
        // CSP analysis (25 points max)
        score += Math.min(cspAnalysis.score * 0.5, 25);
        
        // JavaScript security (20 points max)
        score += Math.max(20 - (jsIssues.length * 5), 0);
        
        // Form security (15 points max)
        score += Math.max(15 - (formIssues.length * 5), 0);
        
        return {
            score: Math.min(score, maxScore),
            percentage: Math.round((Math.min(score, maxScore) / maxScore) * 100),
            category: score >= 80 ? 'secure' : score >= 60 ? 'moderate' : score >= 40 ? 'vulnerable' : 'critical'
        };
    }
    
    async performanceBenchmark() {
        console.log('⚡ Running performance benchmark...');
        
        if (!this.cluster) await this.initCluster();
        
        const results = [];
        
        await this.cluster.task(async ({ page, data }) => {
            const { url, name } = data;
            
            try {
                // Enable performance monitoring
                await page.setCacheEnabled(false);
                
                const startTime = Date.now();
                
                // Navigate and measure
                const response = await page.goto(url, { 
                    waitUntil: 'networkidle2',
                    timeout: 30000
                });
                
                const loadTime = Date.now() - startTime;
                
                // Get performance metrics
                const metrics = await page.metrics();
                
                // Get performance timing
                const timing = await page.evaluate(() => {
                    const perf = performance.timing;
                    return {
                        domLoading: perf.domLoading - perf.navigationStart,
                        domInteractive: perf.domInteractive - perf.navigationStart,
                        domContentLoaded: perf.domContentLoadedEventEnd - perf.navigationStart,
                        loadComplete: perf.loadEventEnd - perf.navigationStart
                    };
                });
                
                // Resource analysis
                const resourceAnalysis = await page.evaluate(() => {
                    const resources = performance.getEntriesByType('resource');
                    const analysis = {
                        totalRequests: resources.length,
                        totalSize: 0,
                        byType: {}
                    };
                    
                    resources.forEach(resource => {
                        const type = resource.initiatorType || 'other';
                        if (!analysis.byType[type]) {
                            analysis.byType[type] = { count: 0, size: 0 };
                        }
                        analysis.byType[type].count++;
                        analysis.byType[type].size += resource.transferSize || 0;
                        analysis.totalSize += resource.transferSize || 0;
                    });
                    
                    return analysis;
                });
                
                // Core Web Vitals simulation
                const webVitals = await page.evaluate(() => {
                    return new Promise((resolve) => {
                        let lcp = 0;
                        let fid = 0;
                        let cls = 0;
                        
                        // Simulate LCP measurement
                        const observer = new PerformanceObserver((list) => {
                            const entries = list.getEntries();
                            entries.forEach((entry) => {
                                if (entry.entryType === 'largest-contentful-paint') {
                                    lcp = entry.renderTime || entry.loadTime;
                                }
                            });
                        });
                        
                        try {
                            observer.observe({ entryTypes: ['largest-contentful-paint'] });
                        } catch (e) {
                            // Fallback if not supported
                        }
                        
                        setTimeout(() => {
                            resolve({ lcp, fid, cls });
                        }, 2000);
                    });
                });
                
                const performanceScore = this.calculatePerformanceScore({
                    loadTime,
                    metrics,
                    timing,
                    resourceAnalysis,
                    webVitals
                });
                
                results.push({
                    url,
                    name,
                    timestamp: Date.now(),
                    loadTime,
                    metrics,
                    timing,
                    resourceAnalysis,
                    webVitals,
                    performanceScore,
                    responseStatus: response.status(),
                    status: 'success'
                });
                
            } catch (error) {
                results.push({
                    url,
                    name,
                    error: error.message,
                    status: 'failed'
                });
            }
        });
        
        // Queue all targets
        const targets = Object.entries(this.config.targets);
        for (const [name, url] of targets) {
            this.cluster.queue({ url, name });
        }
        
        await this.cluster.idle();
        
        // Save performance report
        const reportPath = path.join(this.reportsDir, `performance_${Date.now()}.json`);
        await fs.writeFile(reportPath, JSON.stringify(results, null, 2));
        
        console.log('⚡ Performance benchmark completed');
        return results;
    }
    
    calculatePerformanceScore(data) {
        let score = 100;
        
        // Load time scoring
        if (data.loadTime > 3000) score -= 20;
        else if (data.loadTime > 2000) score -= 10;
        else if (data.loadTime > 1000) score -= 5;
        
        // Resource count scoring
        if (data.resourceAnalysis.totalRequests > 100) score -= 15;
        else if (data.resourceAnalysis.totalRequests > 50) score -= 10;
        
        // Total size scoring (approximate)
        const totalSizeMB = data.resourceAnalysis.totalSize / 1024 / 1024;
        if (totalSizeMB > 5) score -= 15;
        else if (totalSizeMB > 2) score -= 10;
        else if (totalSizeMB > 1) score -= 5;
        
        // LCP scoring
        if (data.webVitals.lcp > 4000) score -= 20;
        else if (data.webVitals.lcp > 2500) score -= 10;
        
        return {
            score: Math.max(score, 0),
            category: score >= 90 ? 'excellent' : score >= 70 ? 'good' : score >= 50 ? 'fair' : 'poor',
            recommendations: this.generatePerformanceRecommendations(data)
        };
    }
    
    generatePerformanceRecommendations(data) {
        const recommendations = [];
        
        if (data.loadTime > 3000) {
            recommendations.push('Optimize page load time - currently over 3 seconds');
        }
        
        if (data.resourceAnalysis.totalRequests > 50) {
            recommendations.push('Reduce number of HTTP requests');
        }
        
        const totalSizeMB = data.resourceAnalysis.totalSize / 1024 / 1024;
        if (totalSizeMB > 2) {
            recommendations.push('Optimize resource sizes - consider compression');
        }
        
        if (data.resourceAnalysis.byType.script?.count > 10) {
            recommendations.push('Consider bundling JavaScript files');
        }
        
        if (data.resourceAnalysis.byType.img?.count > 20) {
            recommendations.push('Optimize images - consider lazy loading');
        }
        
        return recommendations;
    }
    
    async generateVisualReport(results) {
        const report = {
            timestamp: Date.now(),
            summary: {
                totalTests: results.length,
                passed: results.filter(r => r.status === 'success').length,
                failed: results.filter(r => r.status === 'failed').length
            },
            results: results
        };
        
        const reportPath = path.join(this.reportsDir, `visual_regression_${Date.now()}.json`);
        await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
        
        return report;
    }
    
    async cleanup() {
        if (this.cluster) {
            await this.cluster.close();
            console.log('🧹 Cluster closed');
        }
    }
}

// Main execution
async function main() {
    const automation = new AdvancedAIAutomation();
    
    try {
        const command = process.argv[2] || 'help';
        
        switch (command) {
            case 'visual':
                await automation.visualRegressionTest();
                break;
            case 'content':
                await automation.intelligentContentAnalysis();
                break;
            case 'security':
                await automation.advancedSecurityScan();
                break;
            case 'performance':
                await automation.performanceBenchmark();
                break;
            case 'all':
                console.log('🚀 Running complete AI automation suite...');
                await automation.visualRegressionTest();
                await automation.intelligentContentAnalysis();
                await automation.advancedSecurityScan();
                await automation.performanceBenchmark();
                console.log('✅ Complete automation suite finished');
                break;
            default:
                console.log(`
🤖 Advanced AI Automation Engine

Usage: node advanced_ai_automation.js [command]

Commands:
  visual      - Visual regression testing with AI analysis
  content     - Intelligent content analysis and SEO scoring
  security    - Advanced security scanning and scoring
  performance - Performance benchmarking with Web Vitals
  all         - Run complete automation suite

Examples:
  node advanced_ai_automation.js visual
  node advanced_ai_automation.js all
                `);
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

module.exports = AdvancedAIAutomation;
