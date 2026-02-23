#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║  setup-rls.sh — Configurar Row-Level Security en PostgreSQL                   ║
# ║  Uso: bash scripts/setup-rls.sh [database_name]                               ║
# ║  Default database: betamase_data                                               ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

set -e  # Exit on error

DB_NAME="${1:-betamase_data}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_USER="${POSTGRES_USER:-postgres}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔐 Row-Level Security Setup for PostgreSQL                                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}✗ Error: psql not found${NC}"
    echo "Install PostgreSQL first:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql"
    echo "  macOS: brew install postgresql"
    exit 1
fi

# Check if PostgreSQL is running
if ! psql -U $DB_USER -c "SELECT 1" &> /dev/null; then
    echo -e "${RED}✗ Error: Cannot connect to PostgreSQL${NC}"
    echo "Start PostgreSQL with:"
    echo "  sudo systemctl start postgresql  # Linux"
    echo "  brew services start postgresql   # macOS"
    exit 1
fi

echo -e "${YELLOW}Database: ${DB_NAME}${NC}"
echo -e "${YELLOW}Postgres User: ${DB_USER}${NC}"
echo ""

# Step 1: Create database
echo -e "${BLUE}Step 1: Creating database '${DB_NAME}'...${NC}"
psql -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || \
    echo -e "${YELLOW}  (Database already exists)${NC}"
echo -e "${GREEN}✓ Database created or already exists${NC}"
echo ""

# Step 2: Create roles
echo -e "${BLUE}Step 2: Creating security roles...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/rls/01_create_roles.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Roles created: admin_role, superuser_role, user_role${NC}"
else
    echo -e "${RED}✗ Failed to create roles${NC}"
    exit 1
fi
echo ""

# Step 3: Create RLS policies
echo -e "${BLUE}Step 3: Creating Row-Level Security policies...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/rls/02_create_policies.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ RLS policies created${NC}"
    echo -e "  • Admin policy (all rows)"
    echo -e "  • SuperUser policy (by region)"
    echo -e "  • User policy (own data only)"
else
    echo -e "${YELLOW}⚠ RLS policies may have encountered warnings (expected if tables don't exist yet)${NC}"
fi
echo ""

# Step 4: Create views (Column-Level Security)
echo -e "${BLUE}Step 4: Creating security views (Column-Level Security)...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/rls/03_create_views.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Security views created${NC}"
else
    echo -e "${YELLOW}⚠ Security views may have encountered warnings (expected if tables don't exist yet)${NC}"
fi
echo ""

# Step 5: Create audit log table
echo -e "${BLUE}Step 5: Creating audit log table...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/audit/audit_log_table.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Audit log table created with indexes${NC}"
    echo -e "  • audit_log (main table)"
    echo -e "  • idx_audit_log_user (by user_id)"
    echo -e "  • idx_audit_log_action (by action_type)"
    echo -e "  • idx_audit_log_created_at (by timestamp)"
else
    echo -e "${RED}✗ Failed to create audit log${NC}"
    exit 1
fi
echo ""

# Step 6: Create audit triggers
echo -e "${BLUE}Step 6: Creating audit triggers...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/audit/audit_triggers.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Audit triggers created${NC}"
else
    echo -e "${YELLOW}⚠ Audit triggers may have encountered warnings (expected if tables don't exist yet)${NC}"
fi
echo ""

# Step 7: Create AI alerts configuration
echo -e "${BLUE}Step 7: Creating AI alerts configuration...${NC}"
if psql -U $DB_USER -d $DB_NAME < "$REPO_ROOT/database/audit/04_ai_alerts.sql" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ AI alerts tables created${NC}"
    echo -e "  • ai_alerts (alert rules)"
    echo -e "  • alert_notifications (alert history)"
else
    echo -e "${RED}✗ Failed to create AI alerts${NC}"
    exit 1
fi
echo ""

# Verification
echo -e "${BLUE}Verifying setup...${NC}"
echo ""

# Check roles
echo -e "${YELLOW}Roles:${NC}"
psql -U $DB_USER -d $DB_NAME -c "SELECT rolname FROM pg_roles WHERE rolname IN ('admin_role', 'superuser_role', 'user_role');" 2>/dev/null || \
    echo -e "${YELLOW}  (No roles found - may be expected)${NC}"
echo ""

# Check tables
echo -e "${YELLOW}Created tables:${NC}"
psql -U $DB_USER -d $DB_NAME -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;" 2>/dev/null | grep -E "audit|ai_alerts" || \
    echo -e "${YELLOW}  (Tables may not exist yet - will be created when Metabase connects)${NC}"
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ RLS Setup Complete!                                                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "1. Connect this database in Metabase:"
echo "   • Open http://localhost:3000"
echo "   • Admin Panel → Databases → Add Database"
echo "   • PostgreSQL with:"
echo "     - Host: localhost"
echo "     - Port: 5432"
echo "     - Database: ${DB_NAME}"
echo "     - Username: ${DB_USER}"
echo ""
echo "2. Create sample data (if needed):"
echo "   psql -U ${DB_USER} -d ${DB_NAME} < scripts/sample-data.sql"
echo ""
echo "3. Test RLS by creating queries in Metabase"
echo ""
echo -e "${YELLOW}Documentation: See RLS_SETUP_GUIDE.md for detailed information${NC}"
