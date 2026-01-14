#!/bin/bash

# Supabase Setup Script for AI Studio
# This script helps you set up Supabase and configure the frontend

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Supabase Setup for AI Studio ===${NC}\n"

# Step 1: Check if Supabase is already set up
if [ ! -d ".supabase/docker" ]; then
    echo -e "${YELLOW}Step 1: Cloning Supabase repository...${NC}"
    git clone https://github.com/supabase/supabase .supabase
    echo -e "${GREEN}✓ Supabase repository cloned${NC}\n"
else
    echo -e "${GREEN}✓ Supabase repository already exists${NC}\n"
fi

# Step 2: Set up Supabase environment
cd .supabase/docker

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Step 2: Creating Supabase .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .supabase/docker/.env${NC}\n"
else
    echo -e "${GREEN}✓ Supabase .env already exists${NC}\n"
fi

# Ensure email signup works in local self-host without SMTP
echo -e "${YELLOW}Step 2b: Configuring Auth email settings...${NC}"
if grep -q "^ENABLE_EMAIL_AUTOCONFIRM=" .env 2>/dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^ENABLE_EMAIL_AUTOCONFIRM=.*|ENABLE_EMAIL_AUTOCONFIRM=true|" .env
    else
        sed -i "s|^ENABLE_EMAIL_AUTOCONFIRM=.*|ENABLE_EMAIL_AUTOCONFIRM=true|" .env
    fi
else
    echo "ENABLE_EMAIL_AUTOCONFIRM=true" >> .env
fi
echo -e "${GREEN}✓ ENABLE_EMAIL_AUTOCONFIRM=true${NC}\n"

# Extract keys from Supabase .env
echo -e "${YELLOW}Step 3: Reading Supabase keys...${NC}"
ANON_KEY=$(grep "^ANON_KEY=" .env | cut -d'=' -f2)
JWT_SECRET=$(grep "^JWT_SECRET=" .env | cut -d'=' -f2)

if [ -z "$ANON_KEY" ]; then
    echo -e "${RED}Error: ANON_KEY not found in .supabase/docker/.env${NC}"
    exit 1
fi

if [ -z "$JWT_SECRET" ]; then
    echo -e "${RED}Error: JWT_SECRET not found in .supabase/docker/.env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found Supabase keys${NC}\n"

# Step 4: Create frontend .env
cd "$PROJECT_ROOT/frontend"

echo -e "${YELLOW}Step 4: Creating frontend .env file...${NC}"
cat > .env << EOF
# Supabase Configuration
# IMPORTANT: VITE_SUPABASE_URL is left empty to automatically use current hostname
# This allows the app to work from any IP (localhost, LAN, WAN)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=$ANON_KEY
EOF

echo -e "${GREEN}✓ Created frontend/.env${NC}\n"

# Step 5: Update backend .env
cd "$PROJECT_ROOT"

if grep -q "^SUPABASE_JWT_SECRET=" .env 2>/dev/null; then
    echo -e "${YELLOW}Step 5: Updating backend .env...${NC}"
    # Use sed to update the JWT_SECRET
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^SUPABASE_JWT_SECRET=.*|SUPABASE_JWT_SECRET=$JWT_SECRET|" .env
    else
        sed -i "s|^SUPABASE_JWT_SECRET=.*|SUPABASE_JWT_SECRET=$JWT_SECRET|" .env
    fi
    echo -e "${GREEN}✓ Updated SUPABASE_JWT_SECRET in .env${NC}\n"
else
    echo -e "${YELLOW}Step 5: Adding SUPABASE_JWT_SECRET to backend .env...${NC}"
    echo "" >> .env
    echo "# Supabase JWT Secret (added by setup script)" >> .env
    echo "SUPABASE_JWT_SECRET=$JWT_SECRET" >> .env
    echo -e "${GREEN}✓ Added SUPABASE_JWT_SECRET to .env${NC}\n"
fi

# Step 6: Start Supabase
echo -e "${YELLOW}Step 6: Starting Supabase containers...${NC}"
cd "$PROJECT_ROOT/.supabase/docker"

if docker compose version >/dev/null 2>&1; then
    if [ -f "./dev/docker-compose.dev.yml" ]; then
        docker compose -f docker-compose.yml -f ./dev/docker-compose.dev.yml up -d
    else
        docker compose up -d
    fi
elif command -v docker-compose >/dev/null 2>&1; then
    stale_auth_containers=$(docker ps -a --filter name=supabase-auth -q)
    if [ -n "$stale_auth_containers" ]; then
        docker rm -f $stale_auth_containers >/dev/null 2>&1 || true
    fi
    docker-compose up -d
else
    echo -e "${RED}Error: Docker Compose not found. Please install Docker Desktop or docker-compose${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Supabase containers started${NC}\n"

# Step 6b: Apply database schema
echo -e "${YELLOW}Step 6b: Applying Supabase database schema...${NC}"
if [ -f "$PROJECT_ROOT/infra/supabase/schema.sql" ]; then
    docker exec -i supabase-db psql -U postgres -d postgres -v ON_ERROR_STOP=1 < "$PROJECT_ROOT/infra/supabase/schema.sql"
    echo -e "${GREEN}✓ Applied infra/supabase/schema.sql${NC}\n"
else
    echo -e "${YELLOW}Skipped: infra/supabase/schema.sql not found${NC}\n"
fi

# Step 7: Rebuild frontend
echo -e "${YELLOW}Step 7: Rebuilding frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

npm run build

echo -e "${GREEN}✓ Frontend rebuilt with correct configuration${NC}\n"

# Summary
echo -e "${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "Supabase is now running:"
echo -e "  - Supabase Studio: ${YELLOW}http://localhost:3000${NC}"
echo -e "  - Supabase API: ${YELLOW}http://localhost:8000${NC}"
echo -e ""
echo -e "Next steps:"
echo -e "  1. Open Supabase Studio: ${YELLOW}http://localhost:3000${NC}"
echo -e "  2. Go to SQL Editor and run: ${YELLOW}infra/supabase/schema.sql${NC}"
echo -e "  3. Start the backend: ${YELLOW}./start.sh${NC}"
echo -e ""
echo -e "Your app will automatically connect to Supabase at the current hostname."
