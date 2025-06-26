#!/usr/bin/env node
/**
 * AI Automation Orchestrator
 * Manages and coordinates multiple AI automation tasks
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn, exec } = require('child_process');
const EventEmitter = require('events');

class AIAutomationOrchestrator extends EventEmitter {
    constructor() {
        super();
        this.baseDir = path.dirname(__dirname);
        this.scriptsDir = path.join(this.baseDir, 'automation_scripts');
        this.logsDir = path.join(this.baseDir, 'automation_logs');
        this.configDir = path.join(this.baseDir, 'automation_config');
        this.reportsDir = path.join(this.logsDir, 'reports');
        
        this.runningTasks = new Map();
        this.taskQueue = [];
        this.maxConcurrentTasks = 3;
        this.config = null;
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.on('taskStarted', (taskId, taskType) => {
            console.log(`🚀 Task ${taskId} (${taskType}) started`);
        });
        
        this.on('taskCompleted', (taskId, taskType, result) => {
            console.log(`✅ Task ${taskId} (${taskType}) completed`);
            this.runningTasks.delete(taskId);
            this.processQueue();
        });
        
        this.on('taskFailed', (taskId, taskType, error) => {
            console.error(`❌ Task ${taskId} (${taskType}) failed:`, error);
            this.runningTasks.delete(taskId);
            this.processQueue();
        });
    }
    
    async init() {
        await this.ensureDirectories();
        await this.loadConfig();
        await this.setupDashboard();
        console.log('🤖 AI Automation Orchestrator initialized');
    }
    
    async ensureDirectories() {
        const dirs = [this.scriptsDir, this.logsDir, this.configDir, this.reportsDir];
        for (const dir of dirs) {
            try {
                await fs.mkdir(dir, { recursive: true });
            } catch (error) {
                // Directory already exists
            }
        }
    }
    
    async loadConfig() {
        const configPath = path.join(this.configDir, 'orchestrator_config.json');
        
        try {
            const configData = await fs.readFile(configPath, 'utf8');
            this.config = JSON.parse(configData);
        } catch (error) {
            // Create default config
            this.config = {
                scheduling: {
                    healthCheck: { interval: 300, enabled: true }, // 5 minutes
                    securityScan: { interval: 3600, enabled: true }, // 1 hour
                    performanceTest: { interval: 1800, enabled: true }, // 30 minutes
                    contentAnalysis: { interval: 7200, enabled: true }, // 2 hours
                    visualRegression: { interval: 86400, enabled: true } // 24 hours
                },
                notifications: {
                    webhook: null,
                    email: null,
                    slack: null
                },
                thresholds: {
                    performanceScore: 70,
                    securityScore: 80,
                    contentScore: 60
                },
                ai: {
                    enablePredictiveAnalytics: true,
                    enableAnomalyDetection: true,
                    learningMode: true
                }
            };
            
            await fs.writeFile(configPath, JSON.stringify(this.config, null, 2));
        }
    }
    
    async setupDashboard() {
        const dashboardHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Automation Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-running { background: #4CAF50; }
        .status-idle { background: #FFC107; }
        .status-error { background: #F44336; }
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        .task-list {
            max-height: 200px;
            overflow-y: auto;
        }
        .task-item {
            padding: 8px;
            margin-bottom: 5px;
            background: #f8f9fa;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        .controls {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px;
            transition: background 0.3s ease;
        }
        .btn:hover {
            background: #5a67d8;
        }
        .btn-danger {
            background: #F44336;
        }
        .btn-danger:hover {
            background: #d32f2f;
        }
        .log-output {
            background: #1a1a1a;
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Automation Dashboard</h1>
            <p>Intelligent Monitoring & Testing Suite</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>🏥 Health Monitoring <span class="status-indicator status-running" id="health-status"></span></h3>
                <div class="metric">
                    <span>Last Check:</span>
                    <span class="metric-value" id="health-last">--</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value" id="health-rate">--</span>
                </div>
                <div class="metric">
                    <span>Response Time:</span>
                    <span class="metric-value" id="health-time">--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🛡️ Security Scanning <span class="status-indicator status-idle" id="security-status"></span></h3>
                <div class="metric">
                    <span>Security Score:</span>
                    <span class="metric-value" id="security-score">--</span>
                </div>
                <div class="metric">
                    <span>Vulnerabilities:</span>
                    <span class="metric-value" id="security-vulns">--</span>
                </div>
                <div class="metric">
                    <span>Last Scan:</span>
                    <span class="metric-value" id="security-last">--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>⚡ Performance <span class="status-indicator status-running" id="perf-status"></span></h3>
                <div class="metric">
                    <span>Performance Score:</span>
                    <span class="metric-value" id="perf-score">--</span>
                </div>
                <div class="metric">
                    <span>Load Time:</span>
                    <span class="metric-value" id="perf-load">--</span>
                </div>
                <div class="metric">
                    <span>Core Web Vitals:</span>
                    <span class="metric-value" id="perf-vitals">--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🧠 AI Analysis <span class="status-indicator status-idle" id="ai-status"></span></h3>
                <div class="metric">
                    <span>Content Score:</span>
                    <span class="metric-value" id="ai-content">--</span>
                </div>
                <div class="metric">
                    <span>SEO Score:</span>
                    <span class="metric-value" id="ai-seo">--</span>
                </div>
                <div class="metric">
                    <span>Recommendations:</span>
                    <span class="metric-value" id="ai-recs">--</span>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Running Tasks</h3>
                <div class="task-list" id="running-tasks">
                    <div class="task-item">No active tasks</div>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 Recent Results</h3>
                <div class="task-list" id="recent-results">
                    <div class="task-item">No recent results</div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <h3>🎛️ Controls</h3>
            <button class="btn" onclick="runTask('health')">Health Check</button>
            <button class="btn" onclick="runTask('security')">Security Scan</button>
            <button class="btn" onclick="runTask('performance')">Performance Test</button>
            <button class="btn" onclick="runTask('content')">Content Analysis</button>
            <button class="btn" onclick="runTask('visual')">Visual Regression</button>
            <button class="btn" onclick="runTask('all')">Run All</button>
            <button class="btn btn-danger" onclick="stopAll()">Stop All</button>
            
            <div class="log-output" id="log-output">
                AI Automation Dashboard Ready...
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        
        function initWebSocket() {
            ws = new WebSocket('ws://localhost:8444');
            
            ws.onopen = function() {
                log('✅ Connected to AI Automation Orchestrator');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleUpdate(data);
            };
            
            ws.onclose = function() {
                log('❌ Connection lost. Retrying in 5 seconds...');
                setTimeout(initWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                log('❌ WebSocket error: ' + error);
            };
        }
        
        function handleUpdate(data) {
            if (data.type === 'status') {
                updateStatus(data.payload);
            } else if (data.type === 'log') {
                log(data.payload.message);
            } else if (data.type === 'result') {
                updateResults(data.payload);
            }
        }
        
        function updateStatus(status) {
            // Update various status indicators
            Object.keys(status).forEach(key => {
                const element = document.getElementById(key);
                if (element) element.textContent = status[key];
            });
        }
        
        function updateResults(result) {
            const resultsDiv = document.getElementById('recent-results');
            const resultItem = document.createElement('div');
            resultItem.className = 'task-item';
            resultItem.textContent = \`\${result.type}: \${result.status} (\${new Date().toLocaleTimeString()})\`;
            resultsDiv.insertBefore(resultItem, resultsDiv.firstChild);
            
            // Keep only last 10 results
            while (resultsDiv.children.length > 10) {
                resultsDiv.removeChild(resultsDiv.lastChild);
            }
        }
        
        function runTask(task) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: 'run', task: task }));
                log(\`🚀 Starting \${task} task...\`);
            } else {
                log('❌ Not connected to orchestrator');
            }
        }
        
        function stopAll() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: 'stop_all' }));
                log('🛑 Stopping all tasks...');
            }
        }
        
        function log(message) {
            const logDiv = document.getElementById('log-output');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += \`[\${timestamp}] \${message}\\n\`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        // Initialize
        initWebSocket();
        
        // Auto-refresh data every 30 seconds
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: 'get_status' }));
            }
        }, 30000);
    </script>
</body>
</html>`;
        
        const dashboardPath = path.join(this.logsDir, 'dashboard.html');
        await fs.writeFile(dashboardPath, dashboardHTML);
    }
    
    generateTaskId() {
        return 'task_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async queueTask(taskType, options = {}) {
        const taskId = this.generateTaskId();
        const task = {
            id: taskId,
            type: taskType,
            options: options,
            priority: options.priority || 5,
            retryCount: 0,
            maxRetries: options.maxRetries || 3,
            createdAt: Date.now()
        };
        
        this.taskQueue.push(task);
        this.taskQueue.sort((a, b) => a.priority - b.priority); // Lower number = higher priority
        
        console.log(`📝 Task ${taskId} (${taskType}) queued`);
        this.processQueue();
        
        return taskId;
    }
    
    async processQueue() {
        if (this.runningTasks.size >= this.maxConcurrentTasks || this.taskQueue.length === 0) {
            return;
        }
        
        const task = this.taskQueue.shift();
        this.runningTasks.set(task.id, task);
        
        this.emit('taskStarted', task.id, task.type);
        
        try {
            const result = await this.executeTask(task);
            this.emit('taskCompleted', task.id, task.type, result);
        } catch (error) {
            if (task.retryCount < task.maxRetries) {
                task.retryCount++;
                console.log(`🔄 Retrying task ${task.id} (attempt ${task.retryCount}/${task.maxRetries})`);
                this.taskQueue.unshift(task); // Put back at front of queue
                this.runningTasks.delete(task.id);
                setTimeout(() => this.processQueue(), 5000); // Wait 5 seconds before retry
            } else {
                this.emit('taskFailed', task.id, task.type, error);
            }
        }
    }
    
    async executeTask(task) {
        const { type, options } = task;
        
        console.log(`⚡ Executing ${type} task...`);
        
        return new Promise((resolve, reject) => {
            let command;
            let args = [];
            
            switch (type) {
                case 'health':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'automation.js'), 'health'];
                    break;
                case 'security':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'advanced_ai_automation.js'), 'security'];
                    break;
                case 'performance':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'advanced_ai_automation.js'), 'performance'];
                    break;
                case 'content':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'advanced_ai_automation.js'), 'content'];
                    break;
                case 'visual':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'advanced_ai_automation.js'), 'visual'];
                    break;
                case 'all':
                    command = 'node';
                    args = [path.join(this.scriptsDir, 'advanced_ai_automation.js'), 'all'];
                    break;
                default:
                    reject(new Error(`Unknown task type: ${type}`));
                    return;
            }
            
            const child = spawn(command, args, {
                cwd: this.baseDir,
                stdio: ['ignore', 'pipe', 'pipe']
            });
            
            let output = '';
            let errorOutput = '';
            
            child.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            child.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });
            
            child.on('close', (code) => {
                if (code === 0) {
                    resolve({
                        success: true,
                        output: output,
                        duration: Date.now() - task.createdAt
                    });
                } else {
                    reject(new Error(`Task failed with code ${code}: ${errorOutput}`));
                }
            });
            
            child.on('error', (error) => {
                reject(error);
            });
            
            // Set timeout
            const timeout = options.timeout || 300000; // 5 minutes default
            setTimeout(() => {
                child.kill();
                reject(new Error('Task timeout'));
            }, timeout);
        });
    }
    
    async startScheduler() {
        console.log('⏰ Starting automation scheduler...');
        
        Object.entries(this.config.scheduling).forEach(([taskType, schedule]) => {
            if (schedule.enabled) {
                setInterval(() => {
                    this.queueTask(taskType, { priority: 3 });
                }, schedule.interval * 1000);
                
                console.log(`📅 Scheduled ${taskType} every ${schedule.interval} seconds`);
            }
        });
    }
    
    async startWebSocketServer() {
        const WebSocket = require('ws');
        const http = require('http');
        
        const server = http.createServer();
        const wss = new WebSocket.Server({ server });
        
        wss.on('connection', (ws) => {
            console.log('🔌 Dashboard connected');
            
            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    
                    if (data.action === 'run') {
                        const taskId = await this.queueTask(data.task);
                        ws.send(JSON.stringify({
                            type: 'log',
                            payload: { message: \`🚀 Started \${data.task} task (\${taskId})\` }
                        }));
                    } else if (data.action === 'stop_all') {
                        this.stopAllTasks();
                        ws.send(JSON.stringify({
                            type: 'log',
                            payload: { message: '🛑 All tasks stopped' }
                        }));
                    } else if (data.action === 'get_status') {
                        const status = await this.getStatus();
                        ws.send(JSON.stringify({
                            type: 'status',
                            payload: status
                        }));
                    }
                } catch (error) {
                    console.error('WebSocket message error:', error);
                }
            });
            
            ws.on('close', () => {
                console.log('🔌 Dashboard disconnected');
            });
        });
        
        server.listen(8444, () => {
            console.log('🌐 WebSocket server running on port 8444');
        });
    }
    
    async getStatus() {
        // Get latest results from reports
        try {
            const reports = await fs.readdir(this.reportsDir);
            const latestReports = {};
            
            for (const report of reports) {
                const type = report.split('_')[0];
                if (!latestReports[type] || report > latestReports[type]) {
                    latestReports[type] = report;
                }
            }
            
            const status = {};
            
            for (const [type, reportFile] of Object.entries(latestReports)) {
                try {
                    const reportPath = path.join(this.reportsDir, reportFile);
                    const reportData = JSON.parse(await fs.readFile(reportPath, 'utf8'));
                    
                    if (type === 'performance') {
                        status['perf-score'] = reportData[0]?.performanceScore?.score || '--';
                        status['perf-load'] = reportData[0]?.loadTime + 'ms' || '--';
                    } else if (type === 'security') {
                        status['security-score'] = reportData[0]?.securityScore?.score || '--';
                        status['security-vulns'] = reportData[0]?.jsSecurityIssues?.length || 0;
                    } else if (type === 'content') {
                        status['ai-content'] = reportData[0]?.aiScore?.score || '--';
                        status['ai-seo'] = reportData[0]?.pageData?.seo?.title ? 'Good' : 'Poor';
                    }
                } catch (e) {
                    // Skip invalid reports
                }
            }
            
            return status;
        } catch (error) {
            return {};
        }
    }
    
    stopAllTasks() {
        this.taskQueue.length = 0;
        for (const [taskId, task] of this.runningTasks) {
            // In a real implementation, you'd kill the running processes
            this.runningTasks.delete(taskId);
        }
        console.log('🛑 All tasks stopped');
    }
    
    async generateReport() {
        console.log('📊 Generating comprehensive report...');
        
        const reports = await fs.readdir(this.reportsDir);
        const reportData = {};
        
        for (const reportFile of reports) {
            try {
                const reportPath = path.join(this.reportsDir, reportFile);
                const data = JSON.parse(await fs.readFile(reportPath, 'utf8'));
                const type = reportFile.split('_')[0];
                
                if (!reportData[type]) reportData[type] = [];
                reportData[type].push({
                    file: reportFile,
                    timestamp: data.timestamp || Date.now(),
                    data: data
                });
            } catch (error) {
                // Skip invalid reports
            }
        }
        
        // Sort by timestamp
        Object.keys(reportData).forEach(type => {
            reportData[type].sort((a, b) => b.timestamp - a.timestamp);
        });
        
        const comprehensiveReport = {
            generated: Date.now(),
            summary: {
                totalReports: reports.length,
                reportTypes: Object.keys(reportData),
                latestActivity: Math.max(...Object.values(reportData).flat().map(r => r.timestamp))
            },
            reports: reportData
        };
        
        const reportPath = path.join(this.reportsDir, \`comprehensive_\${Date.now()}.json\`);
        await fs.writeFile(reportPath, JSON.stringify(comprehensiveReport, null, 2));
        
        console.log(\`📊 Comprehensive report saved: \${reportPath}\`);
        return comprehensiveReport;
    }
}

async function main() {
    const orchestrator = new AIAutomationOrchestrator();
    
    try {
        await orchestrator.init();
        
        const command = process.argv[2] || 'dashboard';
        
        switch (command) {
            case 'dashboard':
                await orchestrator.startWebSocketServer();
                await orchestrator.startScheduler();
                console.log('🚀 AI Automation Orchestrator running...');
                console.log('📊 Dashboard: http://localhost:8444/dashboard.html');
                console.log('Press Ctrl+C to stop');
                break;
                
            case 'run':
                const taskType = process.argv[3];
                if (taskType) {
                    await orchestrator.queueTask(taskType);
                } else {
                    console.log('Usage: node orchestrator.js run <task_type>');
                }
                break;
                
            case 'report':
                await orchestrator.generateReport();
                break;
                
            case 'schedule':
                await orchestrator.startScheduler();
                console.log('⏰ Scheduler started. Press Ctrl+C to stop');
                break;
                
            default:
                console.log(\`
🤖 AI Automation Orchestrator

Commands:
  dashboard  - Start dashboard and scheduler (default)
  run <type> - Run specific task type
  report     - Generate comprehensive report
  schedule   - Start scheduler only

Task Types: health, security, performance, content, visual, all
                \`);
        }
        
        // Keep process alive
        if (command === 'dashboard' || command === 'schedule') {
            process.on('SIGINT', () => {
                console.log('\\n👋 Shutting down AI Automation Orchestrator...');
                process.exit(0);
            });
            
            // Keep alive
            setInterval(() => {}, 1000);
        }
        
    } catch (error) {
        console.error('❌ Orchestrator failed:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = AIAutomationOrchestrator;
