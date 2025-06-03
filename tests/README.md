# Kanby Test Suite

This directory contains the essential tests for the Kanby terminal Kanban board application.

## Quick Start

### Run All Tests
```bash
# From project root
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v
```

### Run Individual Test Files
```bash
# Core functionality tests
python tests/test_kanby.py

# Data persistence tests
python tests/test_persistence.py

# Project management tests  
python tests/test_project_features.py
```

## Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `test_kanby.py` | Core application functionality | Unit tests for basic operations |
| `test_persistence.py` | Data saving/loading operations | File I/O and data integrity |
| `test_ctrlc.py` | Signal handling and graceful exit | Ctrl+C interrupt handling |
| `test_project_features.py` | Project management features | Project navigation and memory |
| `test_project_rename.py` | Project rename functionality | Rename operations and data integrity |

## Supporting Files

| File | Purpose |
|------|---------|
| `test_manual.md` | Manual testing procedures for UI features |
| `test_projects.json` | Sample test data for project scenarios |
| `__init__.py` | Test package initialization |

## Test Categories

### Core Tests
- **test_kanby.py**: Basic functionality, ID generation, data migration
- **test_persistence.py**: Auto-save, file creation, concurrent operations
- **test_ctrlc.py**: Interrupt handling, graceful shutdown

### Feature Tests  
- **test_project_features.py**: Last project memory, project navigation
- **test_project_rename.py**: Rename operations, duplicate handling

## Running Tests

### All Tests
```bash
python -m pytest tests/
```

### Specific Categories
```bash
# Core functionality
python -m pytest tests/test_kanby.py tests/test_persistence.py

# Project features
python -m pytest tests/test_project_*.py

# Signal handling
python -m pytest tests/test_ctrlc.py
```

## Test Data

Tests use temporary files and directories to ensure isolation:
- No interference between test runs
- Clean state for each test
- Automatic cleanup after completion

### Sample Data Structure
```json
{
  "Project Name": {
    "To Do": [
      {"id": "uuid", "title": "Task", "priority": "High"}
    ],
    "In Progress": [],
    "Done": []
  },
  "_meta": {
    "last_project": "Project Name"
  }
}
```

## Manual Testing

For UI features that require interactive testing, see `test_manual.md` for detailed procedures covering:
- Keyboard navigation
- Project switching
- Data persistence verification
- Error handling scenarios

## Best Practices

- Tests use temporary directories for isolation
- Mock objects are used for curses/UI components
- Each test verifies specific functionality
- Error conditions are tested alongside success cases
- Data integrity is verified after operations