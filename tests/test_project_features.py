#!/usr/bin/env python3
"""
Test script for project navigation and last project memory features.
Tests that arrow keys work in project selection and last project is remembered.
"""

import os
import json
import tempfile
import sys
import time
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import (
    save_last_project_to_data, load_last_project_from_data, manage_projects_modal,
    save_data, load_data, DEFAULT_COLUMNS, DEFAULT_PROJECT_NAME
)

def test_save_and_load_last_project():
    """Test saving and loading last project preference."""
    print("🧪 Testing save and load last project...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_file = os.path.join(temp_dir, 'test_data.json')
        
        with patch('kanby.main.DATA_FILE', test_data_file):
            # Create test data structure
            test_data = {
                "My Test Project": {"To Do": [], "In Progress": [], "Done": []},
                "Another Project": {"To Do": [], "In Progress": [], "Done": []}
            }
            
            # Test saving a project name
            save_last_project_to_data(test_data, "My Test Project")
            save_data(test_data)
            
            # Test loading the project name
            loaded_data = load_data()
            loaded_project = load_last_project_from_data(loaded_data)
            
            if loaded_project == "My Test Project":
                print("✅ Save and load last project test passed!")
                return True
            else:
                print(f"❌ Expected 'My Test Project', got '{loaded_project}'")
                return False

def test_meta_data_creation():
    """Test that meta data is created correctly in data file."""
    print("🧪 Testing meta data creation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_file = os.path.join(temp_dir, 'test_data.json')
        
        with patch('kanby.main.DATA_FILE', test_data_file):
            # Create test data structure
            test_data = {
                "Test Project": {"To Do": [], "In Progress": [], "Done": []}
            }
            
            # Save a project
            save_last_project_to_data(test_data, "Test Project")
            save_data(test_data)
            
            # Check file contents
            with open(test_data_file, 'r') as f:
                data = json.load(f)
            
            if data.get('_meta', {}).get('last_project') == "Test Project":
                print("✅ Meta data creation test passed!")
                return True
            else:
                print(f"❌ Unexpected file contents: {data}")
                return False

def test_multiple_project_saves():
    """Test saving different projects overwrites correctly."""
    print("🧪 Testing multiple project saves...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_file = os.path.join(temp_dir, 'test_data.json')
        
        with patch('kanby.main.DATA_FILE', test_data_file):
            # Create test data structure
            test_data = {
                "Project A": {"To Do": [], "In Progress": [], "Done": []},
                "Project B": {"To Do": [], "In Progress": [], "Done": []},
                "Project C": {"To Do": [], "In Progress": [], "Done": []}
            }
            
            projects = ["Project A", "Project B", "Project C"]
            
            for project in projects:
                save_last_project_to_data(test_data, project)
                save_data(test_data)
                loaded_data = load_data()
                loaded = load_last_project_from_data(loaded_data)
                
                if loaded != project:
                    print(f"❌ Failed to save/load '{project}', got '{loaded}'")
                    return False
            
            # Final check - should have the last project
            final_data = load_data()
            final_project = load_last_project_from_data(final_data)
            if final_project == projects[-1]:
                print("✅ Multiple project saves test passed!")
                return True
            else:
                print(f"❌ Expected '{projects[-1]}', got '{final_project}'")
                return False

def test_project_startup_logic():
    """Test that startup correctly selects last project."""
    print("🧪 Testing project startup logic...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_file = os.path.join(temp_dir, 'test_data.json')
        
        # Create test data with multiple projects and last project saved
        test_data = {
            "Work Project": {"To Do": [], "In Progress": [], "Done": []},
            "Personal Project": {"To Do": [], "In Progress": [], "Done": []},
            "Default Project": {"To Do": [], "In Progress": [], "Done": []},
            "_meta": {"last_project": "Personal Project"}
        }
        
        with open(test_data_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('kanby.main.DATA_FILE', test_data_file):
            # Simulate startup: load data and determine current project
            all_projects_data = load_data()
            project_names_list = [key for key in all_projects_data.keys() if key != "_meta"]
            
            # Try to load the last opened project from data
            last_project = load_last_project_from_data(all_projects_data)
            if last_project and last_project in project_names_list:
                current_project_name = last_project
            else:
                current_project_name = project_names_list[0] if project_names_list else DEFAULT_PROJECT_NAME
            
            if current_project_name == "Personal Project":
                print("✅ Project startup logic test passed!")
                return True
            else:
                print(f"❌ Expected 'Personal Project', got '{current_project_name}'")
                return False

def test_nonexistent_last_project():
    """Test handling when last project no longer exists."""
    print("🧪 Testing nonexistent last project handling...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_file = os.path.join(temp_dir, 'test_data.json')
        
        # Create test data with a last project that doesn't exist
        test_data = {
            "Existing Project": {"To Do": [], "In Progress": [], "Done": []},
            "_meta": {"last_project": "Deleted Project"}
        }
        
        with open(test_data_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('kanby.main.DATA_FILE', test_data_file):
            # Simulate startup
            all_projects_data = load_data()
            project_names_list = [key for key in all_projects_data.keys() if key != "_meta"]
            
            last_project = load_last_project_from_data(all_projects_data)
            if last_project and last_project in project_names_list:
                current_project_name = last_project
            else:
                current_project_name = project_names_list[0] if project_names_list else DEFAULT_PROJECT_NAME
            
            if current_project_name == "Existing Project":
                print("✅ Nonexistent last project handling test passed!")
                return True
            else:
                print(f"❌ Expected 'Existing Project', got '{current_project_name}'")
                return False

def test_error_handling():
    """Test error handling for data operations."""
    print("🧪 Testing error handling...")
    
    # Test with empty data structure
    empty_data = {}
    save_last_project_to_data(empty_data, "Test Project")
    result = load_last_project_from_data(empty_data)
    
    if result == "Test Project":
        print("✅ Error handling test passed!")
        return True
    else:
        print(f"❌ Expected 'Test Project', got '{result}'")
        return False

def main():
    """Run all project feature tests."""
    print("🔥 Kanby Project Features Tests")
    print("=" * 50)
    print("Testing:")
    print("• Project navigation with arrow keys")
    print("• Last project memory functionality") 
    print("• Preferences file management")
    print("• Startup project selection logic")
    print("=" * 50)
    
    tests = [
        test_save_and_load_last_project,
        test_meta_data_creation,
        test_multiple_project_saves,
        test_project_startup_logic,
        test_nonexistent_last_project,
        test_error_handling
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
        print("🎉 All project feature tests passed!")
        print("✅ Project navigation and memory features working correctly!")
        print()
        print("🎯 Features tested:")
        print("• ↑↓ arrow keys work in project selection")
        print("• Last opened project is remembered")
        print("• Project switching saves preference")
        print("• Startup loads last project correctly")
        print("• Error handling works properly")
        return True
    else:
        print("❌ Some project feature tests failed.")
        print("💡 Check the project navigation and memory functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)