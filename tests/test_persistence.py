#!/usr/bin/env python3
"""
Test script to verify data persistence in Kanby.
This test verifies that data is properly saved and loaded.
"""

import os
import json
import tempfile
import sys
import time
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import save_data, load_data, generate_id, DEFAULT_COLUMNS, DEFAULT_PROJECT_NAME

def test_basic_persistence():
    """Test basic save and load functionality."""
    print("🧪 Testing basic persistence...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Create test data
        test_data = {
            "Test Project": {
                "To Do": [
                    {"id": generate_id(), "title": "Test Task 1", "priority": "High"},
                    {"id": generate_id(), "title": "Test Task 2", "priority": "Low"}
                ],
                "In Progress": [
                    {"id": generate_id(), "title": "Working Task", "priority": "Mid"}
                ],
                "Done": []
            }
        }
        
        # Test save and load with temporary file
        with patch('kanby.main.DATA_FILE', temp_file):
            save_data(test_data)
            loaded_data = load_data()
        
        # Verify data matches
        if loaded_data == test_data:
            print("✅ Basic persistence test passed!")
            return True
        else:
            print("❌ Basic persistence test failed!")
            print(f"Expected: {test_data}")
            print(f"Got: {loaded_data}")
            return False
            
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_auto_save_simulation():
    """Simulate the auto-save functionality."""
    print("🧪 Testing auto-save simulation...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Simulate adding tasks one by one (like in the real app)
        with patch('kanby.main.DATA_FILE', temp_file):
            # Start with empty data
            all_projects_data = {DEFAULT_PROJECT_NAME: {col: [] for col in DEFAULT_COLUMNS}}
            
            # Add first task
            task1 = {"id": generate_id(), "title": "First Task", "priority": "High"}
            all_projects_data[DEFAULT_PROJECT_NAME]["To Do"].append(task1)
            save_data(all_projects_data)  # Auto-save
            
            # Verify it persists
            loaded_data = load_data()
            if len(loaded_data[DEFAULT_PROJECT_NAME]["To Do"]) != 1:
                print("❌ First task not saved!")
                return False
            
            # Add second task
            task2 = {"id": generate_id(), "title": "Second Task", "priority": "Mid"}
            all_projects_data[DEFAULT_PROJECT_NAME]["In Progress"].append(task2)
            save_data(all_projects_data)  # Auto-save
            
            # Verify both tasks persist
            loaded_data = load_data()
            if (len(loaded_data[DEFAULT_PROJECT_NAME]["To Do"]) != 1 or 
                len(loaded_data[DEFAULT_PROJECT_NAME]["In Progress"]) != 1):
                print("❌ Second task not saved!")
                return False
            
            print("✅ Auto-save simulation test passed!")
            return True
            
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_file_creation():
    """Test that file is created when it doesn't exist."""
    print("🧪 Testing file creation...")
    
    # Use a non-existent file path
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'new_kanban.json')
    
    try:
        # Load from non-existent file
        with patch('kanby.main.DATA_FILE', temp_file):
            loaded_data = load_data()
            
            # Should return default structure
            if (DEFAULT_PROJECT_NAME in loaded_data and
                all(col in loaded_data[DEFAULT_PROJECT_NAME] for col in DEFAULT_COLUMNS)):
                print("✅ File creation test passed!")
                return True
            else:
                print("❌ File creation test failed!")
                return False
                
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        os.rmdir(temp_dir)

def test_concurrent_operations():
    """Test multiple save/load operations."""
    print("🧪 Testing concurrent operations...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Simulate rapid operations
            for i in range(5):
                # Load current data
                current_data = load_data()
                
                # Add a task
                new_task = {
                    "id": generate_id(), 
                    "title": f"Task {i+1}", 
                    "priority": "Mid"
                }
                current_data[DEFAULT_PROJECT_NAME]["To Do"].append(new_task)
                
                # Save immediately
                save_data(current_data)
                
                # Verify it's there
                reloaded_data = load_data()
                expected_tasks = i + 1
                actual_tasks = len(reloaded_data[DEFAULT_PROJECT_NAME]["To Do"])
                
                if actual_tasks != expected_tasks:
                    print(f"❌ Concurrent operations test failed at iteration {i+1}!")
                    print(f"Expected {expected_tasks} tasks, got {actual_tasks}")
                    return False
            
            print("✅ Concurrent operations test passed!")
            return True
            
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_data_integrity():
    """Test that data integrity is maintained."""
    print("🧪 Testing data integrity...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Create data with special characters and unicode
            test_data = {
                "Project 🚀": {
                    "To Do": [
                        {"id": generate_id(), "title": "Task with émojis 🎯", "priority": "High"},
                        {"id": generate_id(), "title": "Task with unicode: ñáéíóú", "priority": "Low"}
                    ],
                    "In Progress": [],
                    "Done": [
                        {"id": generate_id(), "title": "Completed: Fix «quotes» & symbols", "priority": "Mid"}
                    ]
                }
            }
            
            # Save and reload
            save_data(test_data)
            loaded_data = load_data()
            
            # Check data integrity
            if loaded_data == test_data:
                print("✅ Data integrity test passed!")
                return True
            else:
                print("❌ Data integrity test failed!")
                return False
                
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """Run all persistence tests."""
    print("🔥 Kanby Data Persistence Tests")
    print("=" * 50)
    
    tests = [
        test_basic_persistence,
        test_file_creation, 
        test_auto_save_simulation,
        test_concurrent_operations,
        test_data_integrity
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All persistence tests passed!")
        print("✅ Your data will be saved automatically!")
        return True
    else:
        print("❌ Some tests failed. Data persistence may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)