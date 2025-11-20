# Administrator Manual - Documentation-Tool-Generic

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Target Audience:** System Administrators, IT Support, Deployment Teams

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Maintenance](#maintenance)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)
9. [Backup and Recovery](#backup-and-recovery)
10. [Performance Tuning](#performance-tuning)
11. [Monitoring](#monitoring)
12. [Appendices](#appendices)

---

## Introduction

### Purpose

This manual provides comprehensive guidance for system administrators responsible for deploying, configuring, and maintaining the Documentation-Tool-Generic application in production environments.

### Scope

This manual covers:
- System installation and configuration
- Production deployment procedures
- Security configuration
- Performance optimization
- Maintenance and updates
- Troubleshooting procedures
- Backup and recovery

### Prerequisites

Administrators should have:
- Windows system administration experience
- Python environment management knowledge
- Network configuration understanding
- Security best practices awareness

---

## System Requirements

### Minimum Requirements

**Operating System:**
- Windows 10 (64-bit) or Windows 11 (64-bit)
- Administrator privileges for installation

**Hardware:**
- CPU: Dual-core processor, 2.0 GHz or higher
- RAM: 4 GB minimum, 8 GB recommended
- Storage: 2 GB free disk space (minimum)
- Display: 1280x720 resolution minimum

**Software:**
- Python 3.10 or higher
- Tesseract OCR (version 5.0 or higher)
- Internet connection (for OpenAI API access)

### Recommended Requirements

**Hardware:**
- CPU: Quad-core processor, 3.0 GHz or higher
- RAM: 16 GB
- Storage: 10 GB free disk space (SSD recommended)
- Display: 1920x1080 resolution or higher

**Software:**
- Python 3.11 or higher
- Latest Tesseract OCR version
- Stable internet connection (broadband)

### Network Requirements

**Outbound Connections:**
- HTTPS access to `api.openai.com` (port 443)
- DNS resolution for OpenAI API

**Firewall Configuration:**
- Allow outbound HTTPS connections
- No inbound ports required (desktop application)

---

## Installation

### Pre-Installation Checklist

- [ ] Verify Windows version compatibility
- [ ] Confirm Python 3.10+ installation
- [ ] Verify administrator privileges
- [ ] Check available disk space
- [ ] Verify internet connectivity
- [ ] Prepare OpenAI API key

### Installation Methods

#### Method 1: Standard Installation (Recommended)

**Step 1: Download Application**

```bash
# Clone repository or extract distribution package
git clone <repository-url>
cd Documentation-Tool-Generic
```

**Step 2: Create Virtual Environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Install Tesseract OCR**

1. Download Tesseract OCR installer from:
   https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer with default settings
3. Add to system PATH or configure environment variable:
   ```bash
   setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

**Step 5: Configure Environment**

```bash
# Copy example environment file
copy env.example .env

# Edit .env and configure:
# - OPENAI_API_KEY=your_api_key_here
# - OPENAI_MODEL=gpt-5
# - OCR_LANGUAGE=deu+eng
# - PRIVACY_MASK_ENABLED=true
```

**Step 6: Verify Installation**

```bash
python scripts/validate_startup.py
```

#### Method 2: Silent Installation (Enterprise)

For automated deployment:

```bash
# Silent Python virtual environment creation
python -m venv venv --quiet

# Silent dependency installation
venv\Scripts\activate
pip install -r requirements.txt --quiet --no-warn-script-location

# Configure via environment variables (no .env file needed)
setx OPENAI_API_KEY "your_api_key_here"
setx OPENAI_MODEL "gpt-5"
```

### Post-Installation Verification

**Verify Components:**

```bash
# Check Python version
python --version

# Verify Tesseract installation
tesseract --version

# Test application startup
python main.py --version
```

**Verify Configuration:**

1. Check environment variables are set
2. Verify `.env` file exists and contains API key
3. Test OpenAI API connectivity
4. Verify Tesseract OCR accessibility

---

## Configuration

### Environment Variables

**Required Variables:**

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Optional Variables:**

```env
# AI Configuration
OPENAI_MODEL=gpt-5                    # Model selection
OPENAI_TEMPERATURE=0.7                # Response creativity (0.0-1.0)
OPENAI_MAX_TOKENS=500                 # Maximum response length

# OCR Configuration
OCR_LANGUAGE=deu+eng                  # Language codes (ISO 639-2)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata

# Privacy Configuration
PRIVACY_MASK_ENABLED=true              # Enable privacy masking
PRIVACY_MASK_STYLE=black_rectangle     # Mask style

# Directory Configuration
DATA_DIR=./data                        # Data directory
SESSION_DIR=./data/sessions            # Session storage
SCREENSHOT_DIR=./data/screenshots      # Screenshot storage
OUTPUT_DIR=./data/output               # Output directory
LOG_DIR=./logs                         # Log directory

# Performance Configuration
POLL_INTERVAL=1.0                      # Window polling interval (seconds)
CHANGE_THRESHOLD=0.5                   # Change detection threshold
MAX_CAPTURES_PER_MINUTE=30             # Rate limiting
```

### Configuration Files

#### Trigger Configuration (`config/trigger_config.yml`)

Controls screenshot capture sensitivity:

```yaml
# Polling Configuration
poll_interval: 1.0                    # Check interval (seconds)
min_capture_interval: 2.0             # Minimum time between captures

# Change Detection
change_threshold: 0.5                 # Sensitivity (0.0-1.0)
size_change_threshold: 10             # Pixels for size change detection

# Mouse Interaction
double_click_delay: 0.5               # Double-click detection delay

# Rate Limiting
max_captures_per_minute: 30           # Maximum captures per minute
```

#### Privacy Mask Configuration (`config/privacy_mask.yml`)

Defines sensitive data masking:

```yaml
# Enable automatic detection
auto_detection_enabled: true

# Detection patterns
detection_patterns:
  email: true
  phone: true
  credit_card: false
  ssn: true
  ip_address: false

# Mask rendering style
mask_style: black_rectangle           # Options: black_rectangle, blur, pixelate
blur_intensity: 15                    # Blur intensity (if using blur)

# Static masks (always applied)
masks:
  - type: rectangle
    x: 100
    y: 200
    width: 300
    height: 50
    description: "Username field"
```

#### Cleanup Configuration (`config/cleanup_config.yml`)

Manages file retention:

```yaml
# Enable automatic cleanup
auto_cleanup_enabled: true

# Retention periods (days)
retention_days_screenshots: 30       # Screenshot retention
retention_days_sessions: 90          # Session data retention
retention_days_output: 365           # Output file retention

# Cleanup schedule
cleanup_on_startup: true               # Run cleanup on application start
cleanup_on_shutdown: false            # Run cleanup on application shutdown
```

### Network Configuration

**Proxy Configuration:**

If behind corporate proxy, configure:

```env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1
```

**API Endpoint Configuration:**

For custom OpenAI-compatible endpoints:

```env
OPENAI_API_BASE=https://api.openai.com/v1
```

### Security Configuration

**API Key Security:**

- Store API keys in `.env` file (not in code)
- Use environment variables for production
- Restrict file permissions on `.env` file
- Never commit API keys to version control
- Rotate API keys regularly

**File Permissions:**

```bash
# Restrict .env file access
icacls .env /grant:r "%USERNAME%:R"
icacls .env /deny "Everyone:(R,W)"

# Restrict configuration directory
icacls config /grant:r "%USERNAME%:(OI)(CI)F"
```

---

## Deployment

### Single-User Deployment

**Standard Desktop Deployment:**

1. Install application to user's local directory
2. Configure user-specific `.env` file
3. Create desktop shortcut
4. Configure user permissions

**Deployment Script:**

```batch
@echo off
REM Single-user deployment script

REM Create application directory
mkdir "C:\Program Files\Documentation-Tool-Generic"
xcopy /E /I /Y . "C:\Program Files\Documentation-Tool-Generic"

REM Create desktop shortcut
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Documentation Tool.lnk'); $Shortcut.TargetPath = 'C:\Program Files\Documentation-Tool-Generic\main.py'; $Shortcut.WorkingDirectory = 'C:\Program Files\Documentation-Tool-Generic'; $Shortcut.Save()"

REM Configure environment
copy env.example "C:\Program Files\Documentation-Tool-Generic\.env"
echo Please configure .env file with your OpenAI API key
```

### Multi-User Deployment

**Shared Installation:**

1. Install to shared network location or local Program Files
2. Configure user-specific data directories
3. Set up user profiles with individual configurations
4. Configure shared resources (if applicable)

**Configuration:**

```env
# User-specific data directory
DATA_DIR=%USERPROFILE%\Documents\DocumentationTool\data
SESSION_DIR=%USERPROFILE%\Documents\DocumentationTool\data\sessions
OUTPUT_DIR=%USERPROFILE%\Documents\DocumentationTool\data\output
```

### Enterprise Deployment

**Group Policy Deployment:**

1. Package application as MSI or use deployment tools
2. Deploy via Group Policy or SCCM
3. Configure via Group Policy preferences
4. Distribute API keys securely (via secure key management)

**SCCM Deployment:**

```xml
<!-- Application deployment configuration -->
<Application>
  <Name>Documentation-Tool-Generic</Name>
  <Version>1.0.0</Version>
  <DeploymentType>Install</DeploymentType>
  <InstallCommand>setup.exe /quiet</InstallCommand>
  <UninstallCommand>setup.exe /uninstall /quiet</UninstallCommand>
</Application>
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor log files for errors
- Check disk space usage
- Verify API connectivity

**Weekly:**
- Review session statistics
- Check cleanup job execution
- Verify backup integrity

**Monthly:**
- Update dependencies
- Review security configurations
- Analyze performance metrics
- Update documentation

### Update Procedures

**Application Updates:**

1. Backup current installation
2. Backup configuration files
3. Stop application (if running)
4. Install new version
5. Verify configuration compatibility
6. Test application functionality
7. Restore from backup if issues occur

**Update Script:**

```batch
@echo off
REM Application update script

REM Backup current installation
xcopy /E /I /Y "C:\Program Files\Documentation-Tool-Generic" "C:\Backup\DocumentationTool_%DATE%"

REM Backup configuration
copy "C:\Program Files\Documentation-Tool-Generic\.env" "C:\Backup\DocumentationTool_%DATE%\.env"

REM Install new version
xcopy /E /I /Y . "C:\Program Files\Documentation-Tool-Generic"

REM Restore configuration
copy "C:\Backup\DocumentationTool_%DATE%\.env" "C:\Program Files\Documentation-Tool-Generic\.env"
```

### Dependency Updates

**Python Package Updates:**

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages (use with caution)
pip install --upgrade -r requirements.txt
```

**Tesseract OCR Updates:**

1. Download new Tesseract version
2. Install to same location (or update PATH)
3. Verify language data compatibility
4. Test OCR functionality

### Cleanup Management

**Manual Cleanup:**

```bash
# Run cleanup script
python -m src.utils.cleanup_manager --dry-run  # Preview
python -m src.utils.cleanup_manager            # Execute
```

**Automated Cleanup:**

Configure cleanup in `config/cleanup_config.yml`:

```yaml
auto_cleanup_enabled: true
cleanup_on_startup: true
retention_days_screenshots: 30
retention_days_sessions: 90
```

**Scheduled Cleanup (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly)
4. Set action: Run Python script
5. Configure cleanup command

---

## Security

### Security Best Practices

**API Key Management:**

- Never store API keys in code
- Use environment variables or secure key management
- Rotate API keys regularly
- Monitor API key usage
- Revoke compromised keys immediately

**File System Security:**

- Restrict access to configuration files
- Secure data directories
- Encrypt sensitive data at rest (if required)
- Implement file access auditing

**Network Security:**

- Use HTTPS for API communications
- Verify SSL certificate validity
- Monitor network traffic
- Implement firewall rules

**Application Security:**

- Keep application updated
- Monitor for security vulnerabilities
- Implement least privilege access
- Regular security audits

### Security Configuration

**File Permissions:**

```bash
# Restrict .env file
icacls .env /grant:r "%USERNAME%:R" /deny "Everyone:(R,W)"

# Restrict configuration directory
icacls config /grant:r "%USERNAME%:(OI)(CI)F" /deny "Everyone:(OI)(CI)(R,W)"

# Restrict data directory
icacls data /grant:r "%USERNAME%:(OI)(CI)F" /deny "Everyone:(OI)(CI)(R,W)"
```

**Audit Logging:**

Enable Windows audit logging for:
- File access to `.env` and configuration files
- Application execution
- Data directory access

---

## Troubleshooting

### Common Issues

#### Issue: Application Won't Start

**Symptoms:**
- Application fails to launch
- Error messages on startup
- Python errors

**Diagnosis:**

```bash
# Check Python installation
python --version

# Check dependencies
pip list

# Run validation script
python scripts/validate_startup.py

# Check log files
type logs\ahg.log
```

**Solutions:**
- Verify Python 3.10+ installation
- Reinstall dependencies: `pip install -r requirements.txt`
- Check environment variables
- Review log files for errors

#### Issue: OpenAI API Errors

**Symptoms:**
- API connection failures
- Authentication errors
- Rate limiting errors

**Diagnosis:**

```bash
# Test API connectivity
curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"

# Check API key configuration
echo %OPENAI_API_KEY%

# Verify network connectivity
ping api.openai.com
```

**Solutions:**
- Verify API key is correct and active
- Check internet connectivity
- Verify firewall rules
- Check API usage limits and credits
- Review API error messages in logs

#### Issue: OCR Not Working

**Symptoms:**
- OCR text extraction fails
- Tesseract errors
- No text extracted

**Diagnosis:**

```bash
# Test Tesseract installation
tesseract --version

# Test OCR functionality
tesseract test_image.png output.txt

# Check language data
tesseract --list-langs
```

**Solutions:**
- Verify Tesseract installation
- Check TESSERACT_CMD environment variable
- Verify language data files exist
- Check image quality and format
- Review OCR configuration

#### Issue: Performance Problems

**Symptoms:**
- Slow screenshot capture
- Slow document generation
- High memory usage

**Diagnosis:**

```bash
# Monitor resource usage
tasklist /FI "IMAGENAME eq python.exe"

# Check disk space
dir data\screenshots

# Review performance logs
type logs\ahg.log | findstr "performance"
```

**Solutions:**
- Increase poll_interval in trigger config
- Enable rate limiting
- Clean up old sessions and screenshots
- Optimize cleanup configuration
- Check system resources

### Log Analysis

**Log File Location:**

```
logs/
├── ahg.log              # Main application log
└── ahg_errors.log       # Error log
```

**Log Levels:**

- DEBUG: Detailed diagnostic information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Log Analysis:**

```bash
# View recent errors
type logs\ahg_errors.log

# Search for specific errors
findstr "ERROR" logs\ahg.log

# View last 50 lines
powershell -Command "Get-Content logs\ahg.log -Tail 50"
```

---

## Backup and Recovery

### Backup Strategy

**What to Backup:**

1. **Configuration Files:**
   - `.env` file (API keys)
   - `config/` directory
   - User preferences

2. **Session Data:**
   - `data/sessions/` directory
   - Session JSON files

3. **Generated Documents:**
   - `data/output/` directory
   - Export files

**Backup Frequency:**

- Configuration: Before changes
- Session data: Daily
- Output files: As needed

### Backup Procedures

**Manual Backup:**

```batch
@echo off
REM Backup script

REM Create backup directory
mkdir "C:\Backup\DocumentationTool_%DATE%"

REM Backup configuration
xcopy /E /I /Y config "C:\Backup\DocumentationTool_%DATE%\config"
copy .env "C:\Backup\DocumentationTool_%DATE%\.env"

REM Backup session data
xcopy /E /I /Y data\sessions "C:\Backup\DocumentationTool_%DATE%\sessions"

REM Backup output files
xcopy /E /I /Y data\output "C:\Backup\DocumentationTool_%DATE%\output"
```

**Automated Backup (Task Scheduler):**

1. Create scheduled task
2. Set trigger (daily)
3. Configure backup script
4. Set retention policy

### Recovery Procedures

**Configuration Recovery:**

```batch
REM Restore configuration
copy "C:\Backup\DocumentationTool_DATE\.env" .env
xcopy /E /I /Y "C:\Backup\DocumentationTool_DATE\config" config
```

**Session Recovery:**

1. Application automatically detects recoverable sessions
2. Use Session → Session Recovery menu
3. Select session to recover
4. Validate session integrity
5. Resume or generate documents

**Full Recovery:**

1. Restore application files
2. Restore configuration
3. Restore session data
4. Verify application functionality
5. Test critical workflows

---

## Performance Tuning

### Optimization Strategies

**Screenshot Capture:**

- Increase `poll_interval` for slower workflows
- Adjust `change_threshold` for sensitivity
- Enable rate limiting for high-frequency captures

**OCR Processing:**

- Use appropriate language settings
- Optimize image preprocessing
- Consider OCR caching for repeated screenshots

**Document Generation:**

- Process steps in batches
- Optimize image compression
- Use efficient document templates

**Memory Management:**

- Enable automatic cleanup
- Reduce retention periods
- Monitor memory usage
- Optimize large session handling

### Performance Configuration

**Trigger Configuration:**

```yaml
# Optimize for performance
poll_interval: 2.0                    # Increase for slower systems
change_threshold: 0.7                 # Increase for fewer captures
max_captures_per_minute: 20           # Reduce for performance
```

**Cleanup Configuration:**

```yaml
# Aggressive cleanup for performance
retention_days_screenshots: 7          # Reduce retention
retention_days_sessions: 30           # Reduce retention
auto_cleanup_enabled: true
cleanup_on_startup: true
```

---

## Monitoring

### Key Metrics

**Application Metrics:**

- Session count and duration
- Screenshot capture rate
- Document generation time
- Error rates
- API usage

**System Metrics:**

- CPU usage
- Memory usage
- Disk space usage
- Network usage

### Monitoring Tools

**Windows Performance Monitor:**

- Monitor Python process
- Track memory usage
- Monitor disk I/O
- Track network usage

**Log Monitoring:**

- Monitor log files for errors
- Track API usage
- Monitor performance metrics
- Alert on critical errors

**Custom Monitoring:**

Create monitoring script:

```python
# monitor_health.py
import os
import json
from pathlib import Path

def check_disk_space():
    """Check available disk space"""
    # Implementation

def check_log_errors():
    """Check for recent errors in logs"""
    # Implementation

def check_api_connectivity():
    """Verify API connectivity"""
    # Implementation
```

---

## Appendices

### Appendix A: Command Reference

**Application Commands:**

```bash
# Start application
python main.py

# Validate installation
python scripts/validate_startup.py

# Run cleanup
python -m src.utils.cleanup_manager

# Check version
python main.py --version
```

**Configuration Commands:**

```bash
# Set environment variable
setx OPENAI_API_KEY "your_key"

# Check environment variable
echo %OPENAI_API_KEY%

# Test Tesseract
tesseract --version
```

### Appendix B: File Locations

**Application Files:**

- Application: `C:\Program Files\Documentation-Tool-Generic\`
- Configuration: `config/`
- Data: `data/`
- Logs: `logs/`

**User Data:**

- Sessions: `%USERPROFILE%\Documents\DocumentationTool\data\sessions\`
- Output: `%USERPROFILE%\Documents\DocumentationTool\data\output\`
- Screenshots: `%USERPROFILE%\Documents\DocumentationTool\data\screenshots\`

### Appendix C: Error Codes

**Common Error Codes:**

- `ERR001`: Python version incompatible
- `ERR002`: Missing dependency
- `ERR003`: API key not configured
- `ERR004`: Tesseract not found
- `ERR005`: Disk space insufficient
- `ERR006`: Network connectivity issue
- `ERR007`: Configuration file invalid

### Appendix D: Support Resources

**Documentation:**

- User Manual: `USER_MANUAL.md`
- Developer Guide: `docs/development-guide.md`
- Architecture: `docs/architecture.md`

**External Resources:**

- Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
- OpenAI API: https://platform.openai.com/docs
- Python Documentation: https://docs.python.org/

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Maintained By:** System Administration Team

