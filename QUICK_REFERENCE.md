# Quick Reference - Reverse Ingress-Nginx Infrastructure

## Essential Commands

### Quick Start
```bash
# Windows: Launch
start_ai_automation.bat

# Linux/macOS: Full deployment  
python3 deploy_suite.py

# Individual components
python3 portable_server.py      # Start web server
python3 security_monitor.py     # Launch security dashboard
```

### Configuration
```bash
# Edit Nginx configuration
nano config/nginx.conf

# Update domain settings
python3 setup.py --configure --domain your-domain.com

# Configure SSL certificates
python3 scripts/setup-ssl.py --domain your-domain.com
```

### Monitoring
```bash
# Launch security dashboard
python3 security_monitor.py --dashboard

# Perform health check
curl http://localhost:8080/health

# Tail logs
tail -f logs/nginx/access.log
```

## Default URLs
- **HTTP**: http://localhost:8080
- **HTTPS**: https://localhost:8443  
- **Health Check**: http://localhost:8080/health
- **Metrics**: http://localhost:8080/metrics

## File Structure
```
cert-nginx/
├── README.md              # Documentation
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── config/                # Configuration files
├── data/nginx/            # Nginx configurations
├── automation_scripts/    # Automation scripts
├── logs/                  # Log files
└── scripts/               # Utility scripts
```

## Template Customization

### 1. Domain Configuration
1. Update `data/nginx/*.conf` - Replace `<your_domain>` 
2. Modify `config/services.json` - Define backends
3. Execute `python3 setup.py --configure`

### 2. SSL Certificates
```bash
# Automatic setup with Let's Encrypt
python3 scripts/setup-ssl.py --domain your-domain.com

# Manual setup
cp your.crt certs/server.crt
cp your.key certs/server.key
```

### 3. Backend Services
Edit `config/services.json`:
```json
{
    "services": {
        "api": {
            "upstream": "http://your-backend:8000",
            "health_check": "/health"
        }
    }
}
```

## Troubleshooting

### Port Conflicts
```bash
# Identify port usage
netstat -tulpn | grep :8080

# Change port
python3 portable_server.py --port 8081
```

### SSL Issues
```bash
# Recreate certificates
python3 scripts/setup-ssl.py --regenerate

# Validate SSL
openssl s_client -connect localhost:8443
```

### Permissions (Linux/macOS)
```bash
# Adjust script permissions
chmod +x *.sh scripts/*.sh *.py

# Correct ownership
sudo chown -R $USER:$USER .
```

## Support
- **Documentation**: Refer to README.md
- **Logs**: Check `logs/` directory
- **Debugging**: Use `--debug` flag with Python commands
