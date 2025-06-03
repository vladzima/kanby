# Kanby Development Workflow

## Overview

This guide explains how to develop and test Kanby locally while maintaining the ability to switch between development and production versions.

## Local Development Setup

### 1. Clone and Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/vladzima/kanby.git
cd kanby

# Create dedicated development virtual environment
python -m venv kanby-dev
source kanby-dev/bin/activate  # On Windows: kanby-dev\Scripts\activate

# Install in development mode (editable)
pip install -e .
```

### 2. Development Installation Benefits

Installing with `-e` (editable mode) means:
- Changes to code are immediately reflected
- No need to reinstall after each change
- `kanby` command uses your local development code
- Can modify and test without package rebuilding

## Testing Local Changes

### Run from Development Environment

```bash
# Activate development environment
source kanby-dev/bin/activate

# Test your changes
kanby

# Run specific tests
python tests/test_kanby.py
python -m pytest tests/

# Test with custom data file
kanby --data-file test_data.json
```

### Quick Testing Commands

```bash
# Test basic functionality
python -c "from kanby.main import __version__; print(f'Dev version: {__version__}')"

# Test import and basic functions
python -c "from kanby.main import load_data, save_data; print('Import successful')"

# Run a single test file
python tests/test_project_rename.py
```

## Managing Multiple Environments

### Development Environment (Local Changes)

```bash
# Create and activate dev environment
python -m venv kanby-dev
source kanby-dev/bin/activate
pip install -e .

# Your local changes are active
kanby  # Uses development code
```

### Production Environment (PyPI Version)

```bash
# Create and activate production environment
python -m venv kanby-prod
source kanby-prod/bin/activate
pip install kanby

# Uses latest PyPI version
kanby  # Uses production code
```

### Quick Environment Switching

```bash
# Switch to development
source kanby-dev/bin/activate
which kanby  # Should show path in kanby-dev

# Switch to production
deactivate
source kanby-prod/bin/activate
which kanby  # Should show path in kanby-prod

# Check which version you're using
kanby --version  # Or python -c "from kanby.main import __version__; print(__version__)"
```

## Development Workflow

### 1. Daily Development Cycle

```bash
# Start development session
cd /path/to/kanby
source kanby-dev/bin/activate

# Make changes to code
# ... edit files ...

# Test changes immediately (no reinstall needed)
kanby

# Run tests
python tests/test_kanby.py

# Test specific features
python tests/test_project_rename.py
```

### 2. Testing New Features

```bash
# Create test data for new features
cp tests/test_scroll_data.json test_feature.json

# Test with specific data
kanby --data-file test_feature.json

# Run relevant test suites
python tests/test_compact_priority.py
python tests/test_scroll_indicators.py
```

### 3. Regression Testing

```bash
# Test all core functionality
python tests/test_kanby.py
python tests/test_project_features.py
python tests/test_persistence.py

# Run full test suite
python -m pytest tests/ -v

# Test with production data format
cp ~/.kanby_data.json test_production_data.json
kanby --data-file test_production_data.json
```

## Version Comparison Testing

### Compare Development vs Production

```bash
# Test production version
source kanby-prod/bin/activate
kanby --data-file comparison_test.json
# ... note behavior ...
deactivate

# Test development version
source kanby-dev/bin/activate
kanby --data-file comparison_test.json
# ... compare behavior ...
```

### Verify Version Information

```bash
# Development version
source kanby-dev/bin/activate
python -c "from kanby.main import __version__; print(f'Dev: {__version__}')"

# Production version
source kanby-prod/bin/activate
python -c "from kanby.main import __version__; print(f'Prod: {__version__}')"
```

## Data File Management

### Separate Data for Testing

```bash
# Development data
kanby --data-file dev_data.json

# Production testing data
kanby --data-file prod_test_data.json

# Backup production data before testing
cp ~/.kanby_data.json ~/.kanby_data.json.backup
```

### Test Data Templates

```bash
# Use provided test data
kanby --data-file tests/test_scroll_data.json
kanby --data-file tests/test_projects.json

# Create minimal test data
echo '{"Test Project":{"To Do":[],"In Progress":[],"Done":[]},"_meta":{"last_project":"Test Project"}}' > minimal_test.json
kanby --data-file minimal_test.json
```

## Building and Distribution

### Local Package Building

```bash
# Build package locally
python -m build

# Install local build
pip install dist/kanby-*.whl

# Test local build
kanby --version
```

### Pre-release Testing

```bash
# Create pre-release environment
python -m venv kanby-prerelease
source kanby-prerelease/bin/activate

# Install from local build
pip install dist/kanby-*.whl

# Test thoroughly before PyPI release
kanby
python -c "from kanby.main import __version__; print(__version__)"
```

## Troubleshooting

### Environment Issues

```bash
# Check which Python/pip you're using
which python
which pip
which kanby

# Verify virtual environment
echo $VIRTUAL_ENV

# Reinstall if needed
pip uninstall kanby
pip install -e .  # For development
# or
pip install kanby  # For production
```

### Import Errors

```bash
# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"

# Verify kanby installation
pip show kanby

# Test import manually
python -c "import kanby; print('Import successful')"
```

### Data File Conflicts

```bash
# Check current data file location
ls -la kanby_data.json

# Use explicit data file path
kanby --data-file /full/path/to/test_data.json

# Reset to clean state
rm kanby_data.json
kanby  # Will create new default data
```

## Best Practices

### 1. Environment Naming

- `kanby-dev`: Development with local changes
- `kanby-prod`: Latest PyPI version
- `kanby-test`: Testing specific versions
- `kanby-prerelease`: Testing builds before release

### 2. Data File Organization

```
project/
├── kanby_data.json          # Main development data
├── tests/
│   ├── test_scroll_data.json
│   ├── test_projects.json
│   └── minimal_test.json
├── dev_test.json           # Quick development testing
└── production_backup.json  # Backup of production data
```

### 3. Testing Checklist

Before releasing changes:
- [ ] All existing tests pass
- [ ] New functionality tested
- [ ] Compared with production version
- [ ] Data file compatibility verified
- [ ] No regressions in core features
- [ ] Performance impact assessed

### 4. Quick Commands Reference

```bash
# Activate development
source kanby-dev/bin/activate

# Quick test
kanby --data-file tests/test_scroll_data.json

# Run test suite
python -m pytest tests/

# Check version
python -c "from kanby.main import __version__; print(__version__)"

# Switch to production
deactivate && source kanby-prod/bin/activate
```

This workflow ensures you can develop efficiently while maintaining the ability to test against production versions and verify compatibility.
