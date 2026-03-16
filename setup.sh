#!/bin/bash
# ============================================================
# AlumniConnect — Full Integration Setup Script
# Run this ONCE after extracting both zips
# Usage: bash setup.sh
# ============================================================

set -e  # Exit on any error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_step() { echo -e "\n${BLUE}${BOLD}▶ $1${NC}"; }
print_ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
print_warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; }
print_err()  { echo -e "  ${RED}✗${NC} $1"; }

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   AlumniConnect — Setup Script       ║"
echo "  ║   Django Backend + HTML Frontend     ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# ── Step 1: Check Python ──────────────────────────────────────
print_step "Checking Python version"
if ! command -v python3 &>/dev/null; then
    print_err "Python 3 not found. Install it from https://python.org"
    exit 1
fi
PY_VERSION=$(python3 --version | cut -d' ' -f2)
print_ok "Python $PY_VERSION found"

# ── Step 2: Virtual environment ───────────────────────────────
print_step "Creating virtual environment"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_ok "Virtual environment created at ./venv"
else
    print_warn "Virtual environment already exists, skipping"
fi

# Activate
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || {
    print_err "Could not activate venv. Activate manually: source venv/bin/activate"
    exit 1
}
print_ok "Virtual environment activated"

# ── Step 3: Install dependencies ──────────────────────────────
print_step "Installing Python dependencies"
pip install -q -r requirements.txt
print_ok "All packages installed"

# ── Step 4: Environment file ──────────────────────────────────
print_step "Setting up .env file"
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Generate a random secret key
    SECRET=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(60)))")
    sed -i "s|your-very-long-random-secret-key-here|$SECRET|g" .env
    print_ok ".env created with a generated SECRET_KEY"
    print_warn "Edit .env to add your ANTHROPIC_API_KEY for AI features"
else
    print_warn ".env already exists, keeping it"
fi

# ── Step 5: Merge frontend templates ──────────────────────────
print_step "Merging frontend templates into Django project"

FRONTEND_DIR="alumni_system"   # extracted frontend zip
BACKEND_TEMPLATES="templates"
BACKEND_STATIC="static"

if [ -d "$FRONTEND_DIR/templates" ]; then
    cp -r "$FRONTEND_DIR/templates/"* "$BACKEND_TEMPLATES/" 2>/dev/null || true
    print_ok "HTML templates copied to ./templates/"
else
    print_warn "Frontend templates directory not found at ./$FRONTEND_DIR/templates"
    print_warn "Copy templates manually (see README for details)"
fi

if [ -d "$FRONTEND_DIR/static" ]; then
    cp -r "$FRONTEND_DIR/static/"* "$BACKEND_STATIC/" 2>/dev/null || true
    print_ok "Static files (CSS/JS) copied to ./static/"
else
    print_warn "Frontend static directory not found — CSS/JS may be missing"
fi

# ── Step 6: Database migrations ───────────────────────────────
print_step "Running database migrations"
python manage.py migrate --run-syncdb
print_ok "Database schema created (db.sqlite3)"

# ── Step 7: Seed demo data ────────────────────────────────────
print_step "Seeding demo data"
python manage.py seed_data
print_ok "Demo users, jobs, events created"

# ── Step 8: Collect static files ──────────────────────────────
print_step "Collecting static files"
python manage.py collectstatic --noinput -v 0
print_ok "Static files collected to ./staticfiles/"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════╗"
echo -e "║   ✅  Setup Complete! Run the server:         ║"
echo -e "║                                              ║"
echo -e "║   python manage.py runserver                 ║"
echo -e "║   → http://localhost:8000                    ║"
echo -e "║                                              ║"
echo -e "║   Logins:                                    ║"
echo -e "║   admin/admin123    → /staff/dashboard/      ║"
echo -e "║   alumni1/pass123   → /alumni/dashboard/     ║"
echo -e "║   student1/pass123  → /student/dashboard/    ║"
echo -e "╚══════════════════════════════════════════════╝${NC}"
echo ""
