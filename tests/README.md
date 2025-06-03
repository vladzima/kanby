# Kanby Test Suite

This directory contains all tests for the Kanby terminal Kanban board application.

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

# Project rename functionality
python tests/test_project_rename.py

# Project management features
python tests/test_project_features.py
```

## Test Organization

### Core Tests
| File | Purpose | Type |
|------|---------|------|
| `test_kanby.py` | Core application functionality | Unit Tests |
| `test_persistence.py` | Data saving/loading operations | Integration Tests |
| `test_ctrlc.py` | Signal handling and graceful exit | System Tests |

### Feature Tests
| File | Purpose | Type |
|------|---------|------|
| `test_project_features.py` | Project navigation and memory | Feature Tests |
| `test_project_rename.py` | Project rename functionality | Feature Tests |
| `test_modal_navigation.py` | UI modal interactions | UI Tests |

### Demo Tests
| File | Purpose | Type |
|------|---------|------|
| `test_move_demo.py` | Task movement demonstrations | Demo Tests |
| `test_rename_demo.py` | Project rename demonstrations | Demo Tests |

### Supporting Files
| File | Purpose |
|------|---------|
| `test_manual.md` | Manual testing procedures |
| `test_projects.json` | Sample test data |
| `__init__.py` | Test package initialization |

## Test Categories

### 🔧 Unit Tests
- **Focus**: Individual functions and methods
- **Files**: `test_kanby.py`
- **Run Time**: Fast (< 1 second)
- **Dependencies**: Minimal, uses mocks

### 🔗 Integration Tests
- **Focus**: Component interactions
- **Files**: `test_persistence.py`, `test_project_features.py`
- **Run Time**: Medium (1-5 seconds)
- **Dependencies**: File system operations

### 🎭 Feature Tests
- **Focus**: End-to-end functionality
- **Files**: `test_project_rename.py`, `test_modal_navigation.py`
- **Run Time**: Medium (1-5 seconds)
- **Dependencies**: Full application logic

### 🚀 Demo Tests
- **Focus**: Showcase functionality
- **Files**: `test_*_demo.py`
- **Run Time**: Variable
- **Dependencies**: Interactive demonstrations

## Test Patterns

### Import Pattern
All test files use this pattern to import the kanby module:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from kanby.main import function_name
```

### Data Isolation
Tests use temporary directories to avoid conflicts:
```python
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    test_data_file = os.path.join(temp_dir, 'test_data.json')
    # Test code here
```

### Mock Usage
UI tests mock curses components:
```python
from unittest.mock import patch, MagicMock
with patch('curses.newwin', return_value=mock_win):
    # Test code here
```

## Adding New Tests

### For New Features
1. Create `test_feature_name.py`
2. Include both unit and integration tests
3. Add data integrity verification
4. Test error conditions
5. Create demo script if complex

### Test File Template
```python
#!/usr/bin/env python3
"""
Test script for [feature description].
"""

import os
import sys
import tempfile
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import relevant_functions

def test_basic_functionality():
    """Test basic [feature] functionality."""
    # Test implementation
    pass

def main():
    """Run all [feature] tests."""
    # Test runner implementation
    pass

if __name__ == "__main__":
    main()
```

## Test Data

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

### Test Data Guidelines
- Use descriptive project and task names
- Include various priority levels
- Test empty and populated states
- Include edge cases (special characters, long names)

## Running Specific Test Types

### Unit Tests Only
```bash
python -m pytest tests/test_kanby.py
```

### Feature Tests Only
```bash
python -m pytest tests/test_project_*.py
```

### Demo Tests (Manual)
```bash
python tests/test_rename_demo.py
python tests/test_move_demo.py
```

### UI Tests (May require terminal)
```bash
python tests/test_modal_navigation.py
```

## Troubleshooting

### Import Errors
- Ensure you're running from the project root
- Check that `kanby/` directory exists
- Verify Python path in test files

### Curses Errors in Tests
- Some UI tests require a proper terminal
- Mock curses components for automated testing
- Run manually for full UI testing

### File Permission Errors
- Tests create temporary files
- Ensure write permissions in test directory
- Clean up may be needed after interrupted tests

## Best Practices

### Writing Tests
- **Descriptive Names**: Use clear, descriptive test function names
- **Single Purpose**: Each test should verify one specific behavior
- **Data Isolation**: Use temporary files/directories
- **Error Testing**: Test both success and failure cases
- **Documentation**: Include docstrings explaining test purpose

### Test Data
- **Realistic**: Use realistic project and task names
- **Comprehensive**: Cover edge cases and boundary conditions
- **Clean**: Clean up test data after tests complete
- **Isolated**: Don't depend on external files or state

### Performance
- **Fast Unit Tests**: Keep unit tests under 1 second
- **Parallel Safe**: Tests should not interfere with each other
- **Resource Cleanup**: Always clean up resources
- **Minimal Dependencies**: Avoid unnecessary external dependencies

## Continuous Integration

Tests are designed to run in CI environments:
- No interactive prompts
- Proper exit codes (0 for success, non-zero for failure)
- Clear output formatting
- Minimal external dependencies

## Coverage

The test suite aims for high coverage of:
- ✅ Core data operations (save/load/modify)
- ✅ Project management (create/rename/delete)
- ✅ Task operations (add/edit/move/delete)
- ✅ Error handling and edge cases
- ✅ Data integrity and persistence
- ⚠️ UI interactions (limited by curses testing constraints)