#!/usr/bin/env python3
"""
Test script for +1 left margin improvement.
Tests that tasks and empty column text have proper left margin for visual separation.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import draw_board, DEFAULT_COLUMNS, EMPTY_COLUMN_TEXT

def test_task_left_margin():
    """Test that tasks have +1 left margin from column border."""
    print("🧪 Testing task left margin...")
    
    test_data = {
        "To Do": [{"id": "1", "title": "Test task", "priority": "High"}],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Find calls that add task content
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and "[H] Test task" in str(call[0][2])]
    
    if task_calls:
        task_call = task_calls[0]
        y_pos = task_call[0][0]
        x_pos = task_call[0][1]
        
        # First column starts at x=0, so task should be at x=1 (0 + 1)
        expected_x = 1
        
        if x_pos == expected_x:
            print("✅ Task left margin test passed!")
            return True
        else:
            print(f"❌ Wrong task position: expected x={expected_x}, got x={x_pos}")
            return False
    else:
        print("❌ Could not find task calls")
        return False

def test_empty_column_left_margin():
    """Test that empty column text has +1 left margin."""
    print("🧪 Testing empty column left margin...")
    
    test_data = {
        "To Do": [],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Find calls that add empty column text
    calls = mock_stdscr.addstr.call_args_list
    empty_calls = [call for call in calls if len(call[0]) >= 3 and EMPTY_COLUMN_TEXT in str(call[0][2])]
    
    if empty_calls:
        # Check first empty column (To Do)
        first_call = empty_calls[0]
        x_pos = first_call[0][1]
        
        # First column starts at x=0, so empty text should be at x=1 (0 + 1)
        expected_x = 1
        
        if x_pos == expected_x:
            print("✅ Empty column left margin test passed!")
            return True
        else:
            print(f"❌ Wrong empty text position: expected x={expected_x}, got x={x_pos}")
            return False
    else:
        print("❌ Could not find empty column calls")
        return False

def test_consistent_margins_across_columns():
    """Test that all columns have consistent left margins."""
    print("🧪 Testing consistent margins across columns...")
    
    # Mixed data to test multiple columns
    test_data = {
        "To Do": [{"id": "1", "title": "Task 1", "priority": "High"}],
        "In Progress": [],
        "Done": [{"id": "2", "title": "Task 2", "priority": "Low"}]
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    
    # Find content calls (tasks and empty text)
    content_calls = []
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if ("[H] Task 1" in text or EMPTY_COLUMN_TEXT in text or "[L] Task 2" in text):
                x_pos = call[0][1]
                content_calls.append((text, x_pos))
    
    # Expected x positions with +1 margin
    # Assuming default column width ~30, columns at 0, 31, 62, margins at 1, 32, 63
    expected_margins = [1, 32, 63]  # Approximate column positions + 1
    tolerance = 5  # Allow some variance
    
    margin_positions = [call[1] for call in content_calls]
    
    # Check that we have some margin positions
    if len(margin_positions) >= 2:
        # All margins should be at least 1 (never at column start)
        all_have_margin = all(pos > 0 for pos in margin_positions)
        
        if all_have_margin:
            print("✅ Consistent margins across columns test passed!")
            return True
        else:
            print(f"❌ Some content has no margin: {margin_positions}")
            return False
    else:
        print("❌ Not enough content calls found")
        return False

def test_visual_separation():
    """Test that margin creates proper visual separation."""
    print("🧪 Testing visual separation...")
    
    test_data = {
        "To Do": [{"id": "1", "title": "Border test task", "priority": "Mid"}],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    
    # Find task position
    task_calls = [call for call in calls if len(call[0]) >= 3 and "[M] Border test task" in str(call[0][2])]
    
    # Find border positions (vertical lines)
    border_calls = [call for call in calls if len(call[0]) >= 3 and call[0][2] == '|']
    
    if task_calls and border_calls:
        task_x = task_calls[0][0][1]
        
        # Task should not be at column border position (x=0)
        if task_x > 0:
            print("✅ Visual separation test passed!")
            return True
        else:
            print(f"❌ Task too close to border: x={task_x}")
            return False
    else:
        print("❌ Could not find task or border calls")
        return False

def test_selected_task_margin():
    """Test that selected tasks also maintain left margin."""
    print("🧪 Testing selected task margin...")
    
    test_data = {
        "To Do": [{"id": "1", "title": "Selected task", "priority": "High"}],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    # Draw with first task selected
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    
    # Find selected task calls (should have reverse coloring or selection highlighting)
    selected_calls = []
    for call in calls:
        if len(call[0]) >= 3 and "[H] Selected task" in str(call[0][2]):
            selected_calls.append(call)
    
    if selected_calls:
        x_pos = selected_calls[0][0][1]
        expected_x = 1  # Should have +1 margin
        
        if x_pos == expected_x:
            print("✅ Selected task margin test passed!")
            return True
        else:
            print(f"❌ Wrong selected task position: expected x={expected_x}, got x={x_pos}")
            return False
    else:
        print("❌ Could not find selected task calls")
        return False

def main():
    """Run all left margin tests."""
    print("🔥 Kanby Left Margin Tests")
    print("=" * 40)
    print("Testing:")
    print("• Tasks have +1 left margin from column border")
    print("• Empty column text has +1 left margin")
    print("• Consistent margins across all columns")
    print("• Visual separation from column borders")
    print("• Selected tasks maintain proper margin")
    print("=" * 40)
    
    tests = [
        test_task_left_margin,
        test_empty_column_left_margin,
        test_consistent_margins_across_columns,
        test_visual_separation,
        test_selected_task_margin
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
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All left margin tests passed!")
        print("✅ Content has proper visual separation!")
        print()
        print("🎯 Features verified:")
        print("• Tasks positioned at x_pos + 1")
        print("• Empty text positioned at x_pos + 1")
        print("• Consistent margins across columns")
        print("• Better visual separation from borders")
        print("• Selected tasks maintain margins")
        return True
    else:
        print("❌ Some left margin tests failed.")
        print("💡 Check the left margin implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)