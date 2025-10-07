#!/bin/bash
# setup-env-and-run.sh
# Script to check Docker, WSL, prompt for env vars, and run docker compose up
# Author: TalentSync Team
# Created: October 7, 2025

set -e  # Exit on any error

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_info() {
    echo -e "INFO: $1"
}

# Function to check if Docker is installed
check_docker_installation() {
    print_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker and try again."
        print_info "Visit https://docs.docker.com/get-docker/ for installation instructions."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker is installed but not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is installed and running."
}

# Function to check if running on WSL
check_wsl_environment() {
    print_info "Checking WSL environment..."
    if ! grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null; then
        print_error "This script must be run inside WSL (Windows Subsystem for Linux)."
        print_info "Please run this script from within WSL environment."
        exit 1
    fi
    print_success "Running in WSL environment."
}

# Function to validate environment variable format
validate_env_var() {
    local var_name="$1"
    local var_value="$2"
    
    case "$var_name" in
        "ZOHO_ACCESS_TOKEN")
            # Basic validation: should be non-empty and contain alphanumeric characters
            if [[ ! "$var_value" =~ ^[a-zA-Z0-9._-]+$ ]]; then
                print_error "Invalid Zoho access token format. Should contain only alphanumeric characters, dots, underscores, and hyphens."
                return 1
            fi
            ;;
        "GOOGLE_API_KEY")
            # Basic validation: should be non-empty and start with typical Google API key pattern
            if [[ ! "$var_value" =~ ^[a-zA-Z0-9_-]{20,}$ ]]; then
                print_error "Invalid Google API key format. Should be at least 20 characters of alphanumeric, underscore, or hyphen."
                return 1
            fi
            ;;
        "SYNC_INTERVAL")
            # Should be a positive integer
            if [[ ! "$var_value" =~ ^[1-9][0-9]*$ ]]; then
                print_error "Invalid sync interval. Should be a positive integer (minutes)."
                return 1
            fi
            ;;
    esac
    return 0
}

# Function to prompt for and validate environment variables
collect_environment_variables() {
    print_info "Collecting environment variables..."
    
    # Prompt for Zoho Access Token
    while true; do
        read -p "Enter Zoho Access Token: " ZOHO_ACCESS_TOKEN
        if [[ -z "$ZOHO_ACCESS_TOKEN" ]]; then
            print_error "Zoho Access Token cannot be empty."
            continue
        fi
        if validate_env_var "ZOHO_ACCESS_TOKEN" "$ZOHO_ACCESS_TOKEN"; then
            break
        fi
    done
    
    # Prompt for Google API Key
    while true; do
        read -p "Enter Google API Key: " GOOGLE_API_KEY
        if [[ -z "$GOOGLE_API_KEY" ]]; then
            print_error "Google API Key cannot be empty."
            continue
        fi
        if validate_env_var "GOOGLE_API_KEY" "$GOOGLE_API_KEY"; then
            break
        fi
    done
    
    # Prompt for Sync Interval with default
    while true; do
        read -p "Enter Sync Interval (minutes, default 60): " SYNC_INTERVAL
        SYNC_INTERVAL=${SYNC_INTERVAL:-60}
        if validate_env_var "SYNC_INTERVAL" "$SYNC_INTERVAL"; then
            break
        fi
    done
    
    print_success "Environment variables collected and validated."
}

# Function to export environment variables
export_environment_variables() {
    print_info "Exporting environment variables for Docker Compose..."
    export ZOHO_ACCESS_TOKEN
    export GOOGLE_API_KEY
    export SYNC_INTERVAL
    print_success "Environment variables exported."
}

# Function to check docker-compose.yml exists and run docker compose
run_docker_compose() {
    print_info "Checking for docker-compose.yml..."
    
    if [[ ! -f "docker-compose.yml" ]]; then
        print_error "docker-compose.yml not found in current directory: $(pwd)"
        print_info "Please navigate to the directory containing docker-compose.yml or create one."
        exit 1
    fi
    
    print_success "Found docker-compose.yml"
    print_info "Starting Docker Compose with environment variables:"
    print_info "  ZOHO_ACCESS_TOKEN: [HIDDEN]"
    print_info "  GOOGLE_API_KEY: [HIDDEN]"
    print_info "  SYNC_INTERVAL: ${SYNC_INTERVAL} minutes"
    
    # Run docker compose up
    if docker compose up; then
        print_success "Docker Compose started successfully."
    else
        print_error "Failed to start Docker Compose. Check the logs above for details."
        exit 1
    fi
}

# Function to handle cleanup on script exit
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        print_warning "Script exited with error code $exit_code"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution flow
main() {
    print_info "Starting TalentSync environment setup script..."
    print_info "================================================"
    
    # Step 1: Check Docker installation and status
    check_docker_installation
    
    # Step 2: Check WSL environment
    check_wsl_environment
    
    # Step 3: Collect and validate environment variables
    collect_environment_variables
    
    # Step 4: Export environment variables
    export_environment_variables
    
    # Step 5: Run Docker Compose
    run_docker_compose
    
    print_success "TalentSync environment setup completed successfully!"
}

# Execute main function
main "$@"