#!/usr/bin/env node
/**
 * AI Automation Orchestrator - Fixed Version
 * Manages and coordinates multiple AI automation tasks
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');
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
        this.taskQueue.sort((a, b) => a.priority - b.priority);
        
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
                this.taskQueue.unshift(task);
                this.runningTasks.delete(task.id);
                setTimeout(() => this.processQueue(), 5000);
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
        try {
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
                                payload: { message: `🚀 Started ${data.task} task (${taskId})` }
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
        } catch (error) {
            console.error('Failed to start WebSocket server:', error);
        }
    }
    
    async getStatus() {
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
            this.runningTasks.delete(taskId);
        }
        console.log('🛑 All tasks stopped');
    }
    
    async generateReport() {
        console.log('📊 Generating comprehensive report...');
        
        try {
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
            
            const reportPath = path.join(this.reportsDir, `comprehensive_${Date.now()}.json`);
            await fs.writeFile(reportPath, JSON.stringify(comprehensiveReport, null, 2));
            
            console.log(`📊 Comprehensive report saved: ${reportPath}`);
            return comprehensiveReport;
        } catch (error) {
            console.error('Error generating report:', error);
            return null;
        }
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
                console.log('📊 Dashboard: Open automation_logs/dashboard.html in your browser');
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
                console.log(`
🤖 AI Automation Orchestrator

Commands:
  dashboard  - Start dashboard and scheduler (default)
  run <type> - Run specific task type
  report     - Generate comprehensive report
  schedule   - Start scheduler only

Task Types: health, security, performance, content, visual, all
                `);
        }
        
        // Keep process alive
        if (command === 'dashboard' || command === 'schedule') {
            process.on('SIGINT', () => {
                console.log('\n👋 Shutting down AI Automation Orchestrator...');
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
