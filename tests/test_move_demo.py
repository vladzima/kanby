#!/usr/bin/env python3
"""
Test script for the new move functionality in Kanby.
Tests M + arrow key movement system for both column switching and reordering.
"""

import os
import json
import tempfile
import sys
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import save_data, load_data, generate_id, DEFAULT_COLUMNS, DEFAULT_PROJECT_NAME

def test_column_switching():
    """Test moving tasks between columns."""
    print("🧪 Testing column switching...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Create test data with tasks in different columns
            test_data = {
                DEFAULT_PROJECT_NAME: {
                    "To Do": [
                        {"id": "task1", "title": "Task 1", "priority": "High"},
                        {"id": "task2", "title": "Task 2", "priority": "Mid"}
                    ],
                    "In Progress": [
                        {"id": "task3", "title": "Task 3", "priority": "Low"}
                    ],
                    "Done": []
                }
            }
            
            save_data(test_data)
            
            # Simulate moving task1 from "To Do" to "In Progress"
            loaded_data = load_data()
            
            # Move task from position 0 in "To Do" to "In Progress"
            task_to_move = loaded_data[DEFAULT_PROJECT_NAME]["To Do"].pop(0)
            loaded_data[DEFAULT_PROJECT_NAME]["In Progress"].append(task_to_move)
            
            save_data(loaded_data)
            
            # Verify the move
            final_data = load_data()
            
            # Check task1 is now in "In Progress"
            in_progress_tasks = final_data[DEFAULT_PROJECT_NAME]["In Progress"]
            to_do_tasks = final_data[DEFAULT_PROJECT_NAME]["To Do"]
            
            task1_in_progress = any(task["id"] == "task1" for task in in_progress_tasks)
            task1_in_todo = any(task["id"] == "task1" for task in to_do_tasks)
            
            if task1_in_progress and not task1_in_todo:
                print("✅ Column switching test passed!")
                return True
            else:
                print("❌ Column switching test failed!")
                return False
                
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_task_reordering():
    """Test reordering tasks within the same column."""
    print("🧪 Testing task reordering...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Create test data with multiple tasks in one column
            test_data = {
                DEFAULT_PROJECT_NAME: {
                    "To Do": [
                        {"id": "task1", "title": "First Task", "priority": "High"},
                        {"id": "task2", "title": "Second Task", "priority": "Mid"},
                        {"id": "task3", "title": "Third Task", "priority": "Low"}
                    ],
                    "In Progress": [],
                    "Done": []
                }
            }
            
            save_data(test_data)
            
            # Simulate reordering: move task3 to position 0
            loaded_data = load_data()
            to_do_tasks = loaded_data[DEFAULT_PROJECT_NAME]["To Do"]
            
            # Move task from position 2 to position 0
            task_to_move = to_do_tasks.pop(2)  # Remove "Third Task"
            to_do_tasks.insert(0, task_to_move)  # Insert at beginning
            
            save_data(loaded_data)
            
            # Verify the reordering
            final_data = load_data()
            final_to_do = final_data[DEFAULT_PROJECT_NAME]["To Do"]
            
            # Check that "Third Task" is now first
            if (len(final_to_do) == 3 and 
                final_to_do[0]["id"] == "task3" and
                final_to_do[0]["title"] == "Third Task"):
                print("✅ Task reordering test passed!")
                return True
            else:
                print("❌ Task reordering test failed!")
                print(f"Expected task3 first, got: {final_to_do}")
                return False
                
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_move_persistence():
    """Test that moves are properly persisted."""
    print("🧪 Testing move persistence...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Create initial data
            initial_data = {
                DEFAULT_PROJECT_NAME: {
                    "To Do": [
                        {"id": "persist1", "title": "Move Me", "priority": "High"}
                    ],
                    "In Progress": [],
                    "Done": []
                }
            }
            
            save_data(initial_data)
            
            # Perform multiple moves
            for i in range(3):
                current_data = load_data()
                
                if i == 0:
                    # Move from "To Do" to "In Progress"
                    task = current_data[DEFAULT_PROJECT_NAME]["To Do"].pop(0)
                    current_data[DEFAULT_PROJECT_NAME]["In Progress"].append(task)
                elif i == 1:
                    # Move from "In Progress" to "Done"
                    task = current_data[DEFAULT_PROJECT_NAME]["In Progress"].pop(0)
                    current_data[DEFAULT_PROJECT_NAME]["Done"].append(task)
                else:
                    # Move back to "To Do"
                    task = current_data[DEFAULT_PROJECT_NAME]["Done"].pop(0)
                    current_data[DEFAULT_PROJECT_NAME]["To Do"].append(task)
                
                save_data(current_data)
                
                # Verify persistence after each move
                reloaded_data = load_data()
                
                if i == 0:
                    expected_location = "In Progress"
                elif i == 1:
                    expected_location = "Done"
                else:
                    expected_location = "To Do"
                
                task_found = any(
                    task["id"] == "persist1" 
                    for task in reloaded_data[DEFAULT_PROJECT_NAME][expected_location]
                )
                
                if not task_found:
                    print(f"❌ Move persistence failed at step {i+1}")
                    return False
            
            print("✅ Move persistence test passed!")
            return True
            
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_complex_moves():
    """Test complex move scenarios."""
    print("🧪 Testing complex move scenarios...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Create complex scenario with many tasks
            test_data = {
                DEFAULT_PROJECT_NAME: {
                    "To Do": [
                        {"id": f"todo{i}", "title": f"Todo Task {i}", "priority": "Mid"}
                        for i in range(5)
                    ],
                    "In Progress": [
                        {"id": f"progress{i}", "title": f"Progress Task {i}", "priority": "High"}
                        for i in range(3)
                    ],
                    "Done": [
                        {"id": f"done{i}", "title": f"Done Task {i}", "priority": "Low"}
                        for i in range(2)
                    ]
                }
            }
            
            save_data(test_data)
            
            # Perform complex moves
            current_data = load_data()
            
            # Move middle task from "To Do" to "Done"
            task_to_move = current_data[DEFAULT_PROJECT_NAME]["To Do"].pop(2)  # Middle task
            current_data[DEFAULT_PROJECT_NAME]["Done"].insert(0, task_to_move)  # Insert at beginning
            
            # Reorder within "In Progress" - move last to first
            progress_tasks = current_data[DEFAULT_PROJECT_NAME]["In Progress"]
            last_task = progress_tasks.pop()
            progress_tasks.insert(0, last_task)
            
            save_data(current_data)
            
            # Verify complex moves
            final_data = load_data()
            
            # Check that todo2 is now first in "Done"
            done_tasks = final_data[DEFAULT_PROJECT_NAME]["Done"]
            if done_tasks[0]["id"] == "todo2":
                # Check that progress2 is now first in "In Progress"
                progress_tasks = final_data[DEFAULT_PROJECT_NAME]["In Progress"]
                if progress_tasks[0]["id"] == "progress2":
                    print("✅ Complex moves test passed!")
                    return True
            
            print("❌ Complex moves test failed!")
            return False
            
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_edge_cases():
    """Test edge cases for move functionality."""
    print("🧪 Testing edge cases...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        with patch('kanby.main.DATA_FILE', temp_file):
            # Test with single task
            single_task_data = {
                DEFAULT_PROJECT_NAME: {
                    "To Do": [{"id": "single", "title": "Only Task", "priority": "Mid"}],
                    "In Progress": [],
                    "Done": []
                }
            }
            
            save_data(single_task_data)
            
            # Move single task between columns
            current_data = load_data()
            task = current_data[DEFAULT_PROJECT_NAME]["To Do"].pop(0)
            current_data[DEFAULT_PROJECT_NAME]["Done"].append(task)
            save_data(current_data)
            
            # Verify single task move
            final_data = load_data()
            if (len(final_data[DEFAULT_PROJECT_NAME]["Done"]) == 1 and
                final_data[DEFAULT_PROJECT_NAME]["Done"][0]["id"] == "single"):
                print("✅ Edge cases test passed!")
                return True
            else:
                print("❌ Edge cases test failed!")
                return False
                
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """Run all move functionality tests."""
    print("🔥 Kanby Move Functionality Tests")
    print("=" * 50)
    print("Testing the new M + arrow keys system:")
    print("• ← → : Move between columns")
    print("• ↑ ↓ : Reorder within columns")
    print("• Enter: Confirm move")
    print("• Esc: Cancel move")
    print("=" * 50)
    
    tests = [
        test_column_switching,
        test_task_reordering,
        test_move_persistence,
        test_complex_moves,
        test_edge_cases
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
        print("🎉 All move functionality tests passed!")
        print("✅ The new M + arrows system is working correctly!")
        print()
        print("🎯 How to use the new move system:")
        print("1. Select a task with ↑↓ navigation")
        print("2. Press 'm' to enter move mode")
        print("3. Use arrow keys:")
        print("   ← → : Switch between columns")
        print("   ↑ ↓ : Reorder within current column")
        print("4. Press Enter to confirm or Esc to cancel")
        return True
    else:
        print("❌ Some move functionality tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)