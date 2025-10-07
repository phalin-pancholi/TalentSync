# Quick Start Guide: TalentSync Environment Setup Script

## Overview
The `setup-env-and-run.sh` script automates the process of checking system requirements, collecting environment variables, and starting the TalentSync application using Docker Compose.

## Prerequisites
- Docker installed and running
- Windows Subsystem for Linux (WSL) environment
- Valid Zoho access token
- Valid Google API key

## Usage

### 1. Navigate to Project Root
```bash
cd /home/phill/hackathon/internal_hackathon
```

### 2. Run the Setup Script
```bash
./setup-env-and-run.sh
```

### 3. Follow Interactive Prompts
The script will prompt you for:
- **Zoho Access Token**: Your Zoho API access token
- **Google API Key**: Your Google API key
- **Sync Interval**: Synchronization interval in minutes (default: 60)

## Environment Variable Requirements

### Zoho Access Token
- Format: Alphanumeric characters, dots, underscores, and hyphens
- Example: `1000.**********************`

### Google API Key
- Format: At least 20 characters of alphanumeric, underscore, or hyphen
- Example: `AIzaSy****************************HI`

### Sync Interval
- Format: Positive integer (minutes)
- Default: 60 minutes
- Example: `30`, `120`, `1440`

## What the Script Does

1. **System Checks**
   - Verifies Docker installation and daemon status
   - Confirms WSL environment

2. **Environment Variable Collection**
   - Prompts for required configuration
   - Validates input formats
   - Sets default values where applicable

3. **Docker Compose Execution**
   - Exports environment variables
   - Checks for docker-compose.yml
   - Starts the application stack

## Error Handling

The script provides clear error messages for common issues:
- Missing Docker installation
- Docker daemon not running
- Non-WSL environment
- Invalid environment variable formats
- Missing docker-compose.yml file

## Example Session

```bash
$ ./setup-env-and-run.sh
INFO: Starting TalentSync environment setup script...
================================================
INFO: Checking Docker installation...
SUCCESS: Docker is installed and running.
INFO: Checking WSL environment...
SUCCESS: Running in WSL environment.
INFO: Collecting environment variables...
Enter Zoho Access Token: 1000.**********************
Enter Google API Key: AIzaSy****************************HI
Enter Sync Interval (minutes, default 60): 30
SUCCESS: Environment variables collected and validated.
INFO: Exporting environment variables for Docker Compose...
SUCCESS: Environment variables exported.
INFO: Checking for docker-compose.yml...
SUCCESS: Found docker-compose.yml
INFO: Starting Docker Compose with environment variables:
  ZOHO_ACCESS_TOKEN: [HIDDEN]
  GOOGLE_API_KEY: [HIDDEN]
  SYNC_INTERVAL: 30 minutes
[+] Running 3/3
 ✔ Container backend  Started
 ✔ Container frontend Started
 ✔ Container mongodb  Started
SUCCESS: Docker Compose started successfully!
SUCCESS: TalentSync environment setup completed successfully!
```

## Troubleshooting

### Docker Not Found
```
ERROR: Docker is not installed. Please install Docker and try again.
Visit https://docs.docker.com/get-docker/ for installation instructions.
```
**Solution**: Install Docker Desktop for Windows with WSL2 backend.

### Docker Not Running
```
ERROR: Docker is installed but not running. Please start Docker and try again.
```
**Solution**: Start Docker Desktop application.

### Not in WSL
```
ERROR: This script must be run inside WSL (Windows Subsystem for Linux).
Please run this script from within WSL environment.
```
**Solution**: Open WSL terminal and run the script from there.

### Invalid Environment Variables
```
ERROR: Invalid Zoho access token format. Should contain only alphanumeric characters, dots, underscores, and hyphens.
```
**Solution**: Check your token format and ensure it matches the required pattern.

### Missing docker-compose.yml
```
ERROR: docker-compose.yml not found in current directory: /path/to/dir
Please navigate to the directory containing docker-compose.yml or create one.
```
**Solution**: Navigate to the project root directory containing docker-compose.yml.

## Features

- ✅ Comprehensive system requirement checks
- ✅ Interactive environment variable collection
- ✅ Input validation and format checking
- ✅ Colored output for better readability
- ✅ Detailed error messages and troubleshooting hints
- ✅ Secure handling of sensitive data (tokens are hidden in logs)
- ✅ Default values for optional parameters
- ✅ Graceful error handling and cleanup