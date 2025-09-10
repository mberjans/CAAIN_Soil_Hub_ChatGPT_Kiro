#!/bin/bash

# AFAS Native Development Environment Setup Script
# This script sets up the complete local development environment

set -e  # Exit on any error

echo "🌱 Setting up AFAS Native Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS. Some commands may need adjustment for other systems."
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Homebrew is installed (macOS)
if [[ "$OSTYPE" == "darwin"* ]] && ! command -v brew &> /dev/null; then
    print_error "Homebrew is required but not installed. Please install it first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Note: Using Python for all services - no Node.js needed

# Check if Python 3.11+ is installed
if ! command -v python3.11 &> /dev/null; then
    print_status "Installing Python 3.11..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python@3.11
    else
        print_error "Please install Python 3.11+ manually"
        exit 1
    fi
fi

print_success "Prerequisites check completed"

# Create project directory structure
print_status "Creating project directory structure..."

mkdir -p services/{question-router,recommendation-engine,ai-agent,data-integration,image-analysis,user-management,frontend}
mkdir -p databases/{postgresql,mongodb,redis}
mkdir -p infrastructure/{nginx,monitoring}
mkdir -p logs
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{api,deployment}

print_success "Directory structure created"

# Install and configure databases
print_status "Setting up databases..."

# PostgreSQL
if ! command -v psql &> /dev/null; then
    print_status "Installing PostgreSQL..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install postgresql@15
        brew services start postgresql@15
    else
        print_error "Please install PostgreSQL 15+ manually"
        exit 1
    fi
else
    print_status "PostgreSQL already installed"
fi

# MongoDB
if ! command -v mongosh &> /dev/null; then
    print_status "Installing MongoDB..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew tap mongodb/brew
        brew install mongodb-community@7.0
        brew services start mongodb-community@7.0
    else
        print_error "Please install MongoDB 7.0+ manually"
        exit 1
    fi
else
    print_status "MongoDB already installed"
fi

# Redis
if ! command -v redis-cli &> /dev/null; then
    print_status "Installing Redis..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install redis
        brew services start redis
    else
        print_error "Please install Redis manually"
        exit 1
    fi
else
    print_status "Redis already installed"
fi

# Note: NGINX not needed for local development
# Frontend development server will handle routing via proxy configuration

print_success "Database setup completed"

# Wait for databases to start
print_status "Waiting for databases to start..."
sleep 5

# Create PostgreSQL database and user
print_status "Setting up PostgreSQL database..."
createdb afas_db 2>/dev/null || print_warning "Database afas_db may already exist"
psql -d afas_db -c "CREATE USER afas_user WITH PASSWORD 'afas_password';" 2>/dev/null || print_warning "User afas_user may already exist"
psql -d afas_db -c "GRANT ALL PRIVILEGES ON DATABASE afas_db TO afas_user;" 2>/dev/null || true

print_success "Database configuration completed"

print_success "🎉 AFAS Native Development Environment setup completed!"
print_status "Next steps:"
echo "  1. Run './setup-services.sh' to initialize all microservices"
echo "  2. Run './start-all.sh' to start all services"
echo "  3. Visit http://localhost to access the application"