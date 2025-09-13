#!/bin/bash

# AFAS Database Setup Script
# Autonomous Farm Advisory System
# Version: 1.0
# Date: December 2024

set -e  # Exit on any error

echo "🌾 AFAS Database Setup Starting..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
POSTGRES_DB="afas_db"
POSTGRES_USER="afas_user"
POSTGRES_PASSWORD="afas_password_2024"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"

MONGODB_DB="afas_db"
MONGODB_HOST="localhost"
MONGODB_PORT="27017"

REDIS_HOST="localhost"
REDIS_PORT="6379"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a service is running
service_running() {
    if command_exists systemctl; then
        systemctl is-active --quiet "$1" 2>/dev/null
    elif command_exists brew; then
        brew services list | grep "$1" | grep -q "started"
    else
        pgrep -f "$1" >/dev/null 2>&1
    fi
}

# Function to start a service
start_service() {
    local service=$1
    echo -e "${BLUE}Starting $service...${NC}"
    
    if command_exists systemctl; then
        sudo systemctl start "$service"
        sudo systemctl enable "$service"
    elif command_exists brew; then
        brew services start "$service"
    else
        echo -e "${YELLOW}Please start $service manually${NC}"
        return 1
    fi
}

# Function to install PostgreSQL
install_postgresql() {
    echo -e "${BLUE}Installing PostgreSQL...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install postgresql@15 postgis
            brew services start postgresql@15
        else
            echo -e "${RED}Homebrew not found. Please install PostgreSQL manually.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib postgis postgresql-15-postgis-3
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        elif command_exists yum; then
            sudo yum install -y postgresql-server postgresql-contrib postgis
            sudo postgresql-setup initdb
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        else
            echo -e "${RED}Package manager not supported. Please install PostgreSQL manually.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Operating system not supported. Please install PostgreSQL manually.${NC}"
        exit 1
    fi
}

# Function to install MongoDB
install_mongodb() {
    echo -e "${BLUE}Installing MongoDB...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew tap mongodb/brew
            brew install mongodb-community
            brew services start mongodb/brew/mongodb-community
        else
            echo -e "${RED}Homebrew not found. Please install MongoDB manually.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
            echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
            sudo apt-get update
            sudo apt-get install -y mongodb-org
            sudo systemctl start mongod
            sudo systemctl enable mongod
        else
            echo -e "${RED}Package manager not supported. Please install MongoDB manually.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Operating system not supported. Please install MongoDB manually.${NC}"
        exit 1
    fi
}

# Function to install Redis
install_redis() {
    echo -e "${BLUE}Installing Redis...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install redis
            brew services start redis
        else
            echo -e "${RED}Homebrew not found. Please install Redis manually.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y redis-server
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
        elif command_exists yum; then
            sudo yum install -y redis
            sudo systemctl start redis
            sudo systemctl enable redis
        else
            echo -e "${RED}Package manager not supported. Please install Redis manually.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Operating system not supported. Please install Redis manually.${NC}"
        exit 1
    fi
}

# Check and install PostgreSQL
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if ! command_exists psql; then
    echo -e "${YELLOW}PostgreSQL not found. Installing...${NC}"
    install_postgresql
else
    echo -e "${GREEN}PostgreSQL found${NC}"
fi

# Check and install MongoDB
echo -e "${YELLOW}Checking MongoDB...${NC}"
if ! command_exists mongosh && ! command_exists mongo; then
    echo -e "${YELLOW}MongoDB not found. Installing...${NC}"
    install_mongodb
else
    echo -e "${GREEN}MongoDB found${NC}"
fi

# Check and install Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if ! command_exists redis-cli; then
    echo -e "${YELLOW}Redis not found. Installing...${NC}"
    install_redis
else
    echo -e "${GREEN}Redis found${NC}"
fi

# Start services if not running
echo -e "${YELLOW}Checking database services...${NC}"

if ! service_running postgresql; then
    start_service postgresql
fi

if ! service_running mongod && ! service_running mongodb-community; then
    if command_exists brew; then
        start_service mongodb/brew/mongodb-community
    else
        start_service mongod
    fi
fi

if ! service_running redis; then
    if command_exists brew; then
        start_service redis
    else
        start_service redis-server
    fi
fi

# Wait for services to start
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 5

# Setup PostgreSQL
echo -e "${YELLOW}Setting up PostgreSQL database...${NC}"

# Create user and database
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with Homebrew PostgreSQL
    createuser -s "$POSTGRES_USER" 2>/dev/null || echo "User already exists"
    createdb "$POSTGRES_DB" -O "$POSTGRES_USER" 2>/dev/null || echo "Database already exists"
    
    # Set password
    psql -d postgres -c "ALTER USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD';" 2>/dev/null || true
else
    # Linux
    sudo -u postgres createuser -s "$POSTGRES_USER" 2>/dev/null || echo "User already exists"
    sudo -u postgres createdb "$POSTGRES_DB" -O "$POSTGRES_USER" 2>/dev/null || echo "Database already exists"
    
    # Set password
    sudo -u postgres psql -c "ALTER USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD';" 2>/dev/null || true
fi

# Run PostgreSQL schema
echo -e "${BLUE}Creating PostgreSQL schema...${NC}"
export PGPASSWORD="$POSTGRES_PASSWORD"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$(dirname "$0")/postgresql/schema.sql"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}PostgreSQL schema created successfully${NC}"
else
    echo -e "${RED}Failed to create PostgreSQL schema${NC}"
    exit 1
fi

# Setup MongoDB
echo -e "${YELLOW}Setting up MongoDB database...${NC}"

# Check if mongosh is available, otherwise use mongo
if command_exists mongosh; then
    MONGO_CMD="mongosh"
else
    MONGO_CMD="mongo"
fi

# Run MongoDB schema
echo -e "${BLUE}Creating MongoDB collections and indexes...${NC}"
$MONGO_CMD --host "$MONGODB_HOST:$MONGODB_PORT" "$(dirname "$0")/mongodb/schema.js"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}MongoDB schema created successfully${NC}"
else
    echo -e "${RED}Failed to create MongoDB schema${NC}"
    exit 1
fi

# Setup Redis
echo -e "${YELLOW}Setting up Redis...${NC}"

# Copy Redis configuration
if [ -f "$(dirname "$0")/redis/redis.conf" ]; then
    echo -e "${BLUE}Copying Redis configuration...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        REDIS_CONF_DIR="/usr/local/etc"
        if [ -d "/opt/homebrew/etc" ]; then
            REDIS_CONF_DIR="/opt/homebrew/etc"
        fi
    else
        # Linux
        REDIS_CONF_DIR="/etc/redis"
    fi
    
    if [ -w "$REDIS_CONF_DIR" ]; then
        cp "$(dirname "$0")/redis/redis.conf" "$REDIS_CONF_DIR/redis.conf"
        echo -e "${GREEN}Redis configuration copied${NC}"
    else
        echo -e "${YELLOW}Cannot copy Redis config to $REDIS_CONF_DIR (permission denied)${NC}"
        echo -e "${YELLOW}Please copy $(dirname "$0")/redis/redis.conf manually${NC}"
    fi
fi

# Test Redis connection
echo -e "${BLUE}Testing Redis connection...${NC}"
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Redis connection successful${NC}"
else
    echo -e "${RED}Failed to connect to Redis${NC}"
    exit 1
fi

# Create environment file
echo -e "${YELLOW}Creating environment configuration...${NC}"
cat > "$(dirname "$0")/../.env.database" << EOF
# AFAS Database Configuration
# Generated on $(date)

# PostgreSQL Configuration
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB

# MongoDB Configuration
MONGODB_HOST=$MONGODB_HOST
MONGODB_PORT=$MONGODB_PORT
MONGODB_DB=$MONGODB_DB
MONGODB_URL=mongodb://$MONGODB_HOST:$MONGODB_PORT/$MONGODB_DB

# Redis Configuration
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT

# Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Cache Settings
CACHE_TTL_DEFAULT=3600
CACHE_TTL_WEATHER=3600
CACHE_TTL_SOIL=86400
CACHE_TTL_RECOMMENDATIONS=21600
EOF

echo -e "${GREEN}Environment configuration created at .env.database${NC}"

# Verify all connections
echo -e "${YELLOW}Verifying database connections...${NC}"

# Test PostgreSQL
echo -e "${BLUE}Testing PostgreSQL connection...${NC}"
export PGPASSWORD="$POSTGRES_PASSWORD"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT version();" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
else
    echo -e "${RED}✗ PostgreSQL connection failed${NC}"
fi

# Test MongoDB
echo -e "${BLUE}Testing MongoDB connection...${NC}"
$MONGO_CMD --host "$MONGODB_HOST:$MONGODB_PORT" --eval "db.adminCommand('ping')" "$MONGODB_DB" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ MongoDB connection successful${NC}"
else
    echo -e "${RED}✗ MongoDB connection failed${NC}"
fi

# Test Redis
echo -e "${BLUE}Testing Redis connection...${NC}"
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Redis connection successful${NC}"
else
    echo -e "${RED}✗ Redis connection failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 AFAS Database Setup Complete!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}Database Information:${NC}"
echo "• PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "• MongoDB: $MONGODB_HOST:$MONGODB_PORT/$MONGODB_DB"
echo "• Redis: $REDIS_HOST:$REDIS_PORT"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "• Environment file: .env.database"
echo "• PostgreSQL schema: databases/postgresql/schema.sql"
echo "• MongoDB schema: databases/mongodb/schema.js"
echo "• Redis config: databases/redis/redis.conf"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Source the environment file: source .env.database"
echo "2. Update your application configuration to use these databases"
echo "3. Run your application tests to verify connectivity"
echo ""
echo -e "${GREEN}Happy farming! 🌾${NC}"