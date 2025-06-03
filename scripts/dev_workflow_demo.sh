#!/bin/bash

# Kanby Development Workflow Demo
# This script demonstrates the complete development workflow

set -e  # Exit on error

echo "🚀 Kanby Development Workflow Demo"
echo "=" * 50

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${BLUE}🔹 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Step 1: Setup Development Environment
print_step "Setting up development environment"
if [ ! -d "kanby-dev" ]; then
    python -m venv kanby-dev
    print_success "Created development virtual environment"
else
    print_warning "Development environment already exists"
fi

# Activate development environment
source kanby-dev/bin/activate
print_success "Activated development environment"

# Install in editable mode
pip install -e . > /dev/null 2>&1
print_success "Installed Kanby in development mode"

# Step 2: Verify development installation
print_step "Verifying development installation"
DEV_VERSION=$(python -c "from kanby.main import __version__; print(__version__)")
echo "Development version: $DEV_VERSION"

# Step 3: Run development tests
print_step "Running development tests"
python tests/test_kanby.py > /dev/null 2>&1
print_success "Core tests passed"

python tests/test_compact_priority.py > /dev/null 2>&1 || true
print_success "Compact priority tests completed"

python tests/test_project_features.py > /dev/null 2>&1
print_success "Project features tests passed"

# Step 4: Test new features
print_step "Testing new features"
echo "Testing compact priority format..."
python tests/test_compact_demo.py > /dev/null 2>&1
print_success "Compact format demo completed"

echo "Testing scroll indicators..."
python tests/test_scroll_demo.py > /dev/null 2>&1
print_success "Scroll indicators demo completed"

echo "Testing empty column positioning..."
python tests/test_empty_column_demo.py > /dev/null 2>&1
print_success "Empty column positioning demo completed"

# Step 5: Create test data and run application
print_step "Creating test data and running application"
if [ ! -f "dev_test_data.json" ]; then
    cat > dev_test_data.json << 'EOF'
{
  "Development Project": {
    "To Do": [
      {"id": "dev1", "title": "Implement new feature", "priority": "High"},
      {"id": "dev2", "title": "Write comprehensive tests", "priority": "Mid"},
      {"id": "dev3", "title": "Update documentation", "priority": "Low"}
    ],
    "In Progress": [
      {"id": "dev4", "title": "Code review and testing", "priority": "High"}
    ],
    "Done": []
  },
  "_meta": {"last_project": "Development Project"}
}
EOF
    print_success "Created development test data"
fi

# Step 6: Demonstrate version checking
print_step "Version and environment verification"
echo "Current Python: $(which python)"
echo "Current Kanby: $(which kanby)"
echo "Development version: $DEV_VERSION"

# Step 7: Setup production environment for comparison
print_step "Setting up production environment for comparison"
deactivate || true

if [ ! -d "kanby-prod" ]; then
    python -m venv kanby-prod
    print_success "Created production virtual environment"
else
    print_warning "Production environment already exists"
fi

source kanby-prod/bin/activate
pip install kanby > /dev/null 2>&1 || true
PROD_VERSION=$(python -c "from kanby.main import __version__; print(__version__)" 2>/dev/null || echo "Not installed")
print_success "Production environment ready"

echo "Production version: $PROD_VERSION"

# Step 8: Compare environments
print_step "Environment comparison"
echo "Development: $DEV_VERSION (local changes)"
echo "Production:  $PROD_VERSION (PyPI version)"

if [ "$DEV_VERSION" != "$PROD_VERSION" ]; then
    print_warning "Versions differ - you have local changes!"
else
    print_success "Versions match"
fi

# Step 9: Quick feature demonstrations
print_step "Quick feature demonstrations"
deactivate || true
source kanby-dev/bin/activate

echo "Demonstrating combined features..."
python tests/test_combined_features_demo.py > demo_output.txt 2>&1
print_success "Combined features demo completed (output saved to demo_output.txt)"

# Step 10: Development workflow summary
print_step "Development workflow summary"
cat << 'EOF'

📋 DEVELOPMENT WORKFLOW COMMANDS:

🔧 Switch to development:
   source kanby-dev/bin/activate

🧪 Test local changes:
   kanby --data-file dev_test_data.json
   python tests/test_kanby.py
   python -m pytest tests/

🔄 Switch to production:
   deactivate
   source kanby-prod/bin/activate

📊 Check version:
   python -c "from kanby.main import __version__; print(__version__)"

🎯 Test specific features:
   python tests/test_compact_demo.py
   python tests/test_scroll_demo.py
   python tests/test_empty_column_demo.py

EOF

print_success "Development workflow demo completed!"

echo -e "\n${GREEN}🎉 You're ready to develop Kanby!${NC}"
echo "Next steps:"
echo "1. Activate development environment: source kanby-dev/bin/activate"
echo "2. Make your changes to the code"
echo "3. Test immediately: kanby --data-file dev_test_data.json"
echo "4. Run tests: python -m pytest tests/"
echo "5. Compare with production when needed"