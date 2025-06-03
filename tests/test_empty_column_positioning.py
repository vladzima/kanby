#!/usr/bin/env python3
"""
Test script for empty column positioning fix.
Tests that "No tasks" text is aligned with task positioning.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import draw_board, DEFAULT_COLUMNS, EMPTY_COLUMN_TEXT

def test_empty_column_positioning():
    """Test that empty column text is positioned like tasks."""
    print("🧪 Testing empty column positioning...")
    
    # Create test data with empty columns
    test_data = {
        "To Do": [],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Find calls that add the empty column text
    calls = mock_stdscr.addstr.call_args_list
    empty_text_calls = [call for call in calls if len(call[0]) >= 3 and EMPTY_COLUMN_TEXT in str(call[0][2])]
    
    if len(empty_text_calls) >= 3:  # Should be one for each column
        # Check positioning of first empty column text
        first_call = empty_text_calls[0]
        y_pos = first_call[0][0]
        x_pos = first_call[0][1]
        
        # Should be positioned at task_start_y (which is header_y + 2 = 4)
        expected_y = 4  # header_y=2, +2 for task_start_y
        expected_x = 0   # First column starts at x=0
        
        if y_pos == expected_y and x_pos == expected_x:
            print("✅ Empty column positioning test passed!")
            return True
        else:
            print(f"❌ Wrong positioning: expected ({expected_y}, {expected_x}), got ({y_pos}, {x_pos})")
            return False
    else:
        print(f"❌ Expected 3 empty column texts, found {len(empty_text_calls)}")
        return False

def test_empty_vs_task_alignment():
    """Test that empty text aligns with where first task would be."""
    print("🧪 Testing empty text vs task alignment...")
    
    # Test data with one column empty, one with task
    test_data = {
        "To Do": [{"id": "1", "title": "Test task", "priority": "High"}],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    
    # Find task position
    task_calls = [call for call in calls if len(call[0]) >= 3 and "[H] Test task" in str(call[0][2])]
    
    # Find empty column position
    empty_calls = [call for call in calls if len(call[0]) >= 3 and EMPTY_COLUMN_TEXT in str(call[0][2])]
    
    if task_calls and empty_calls:
        task_y = task_calls[0][0][0]
        empty_y = empty_calls[0][0][0]
        
        if task_y == empty_y:
            print("✅ Empty text vs task alignment test passed!")
            return True
        else:
            print(f"❌ Misaligned: task at y={task_y}, empty text at y={empty_y}")
            return False
    else:
        print("❌ Could not find both task and empty text calls")
        return False

def test_no_extra_margins():
    """Test that empty text has no extra left margins."""
    print("🧪 Testing no extra margins...")
    
    test_data = {
        "To Do": [],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    empty_calls = [call for call in calls if len(call[0]) >= 3 and EMPTY_COLUMN_TEXT in str(call[0][2])]
    
    # Check x positions for each column
    expected_x_positions = [0, 31, 62]  # Approximate column positions
    tolerance = 5  # Allow some variance
    
    for i, call in enumerate(empty_calls[:3]):
        x_pos = call[0][1]
        expected_x = expected_x_positions[i]
        
        if abs(x_pos - expected_x) <= tolerance:
            continue
        else:
            print(f"❌ Column {i} wrong x position: expected ~{expected_x}, got {x_pos}")
            return False
    
    print("✅ No extra margins test passed!")
    return True

def test_visual_consistency():
    """Test visual consistency with task positioning."""
    print("🧪 Testing visual consistency...")
    
    # Create mixed scenario
    test_data = {
        "To Do": [{"id": "1", "title": "First task", "priority": "High"}],
        "In Progress": [],
        "Done": [{"id": "2", "title": "Completed task", "priority": "Low"}]
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    
    # Find all content calls (tasks and empty text)
    content_calls = []
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[H] First task" in text or EMPTY_COLUMN_TEXT in text or "[L] Completed task" in text:
                content_calls.append((call[0][0], call[0][1], text))
    
    # All content should be on the same y level
    if content_calls:
        y_positions = [call[0] for call in content_calls]
        if len(set(y_positions)) == 1:  # All same y position
            print("✅ Visual consistency test passed!")
            return True
        else:
            print(f"❌ Inconsistent y positions: {set(y_positions)}")
            return False
    else:
        print("❌ No content calls found")
        return False

def test_empty_column_text_content():
    """Test that empty column text is correct."""
    print("🧪 Testing empty column text content...")
    
    test_data = {
        "To Do": [],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    empty_calls = [call for call in calls if len(call[0]) >= 3 and EMPTY_COLUMN_TEXT in str(call[0][2])]
    
    # Should have exactly 3 empty column texts
    if len(empty_calls) == 3:
        # Check that all contain the correct text
        for call in empty_calls:
            if EMPTY_COLUMN_TEXT not in str(call[0][2]):
                print(f"❌ Wrong empty text content: {call[0][2]}")
                return False
        
        print("✅ Empty column text content test passed!")
        return True
    else:
        print(f"❌ Expected 3 empty column texts, found {len(empty_calls)}")
        return False

def main():
    """Run all empty column positioning tests."""
    print("🔥 Kanby Empty Column Positioning Tests")
    print("=" * 50)
    print("Testing:")
    print("• Empty column text positioned like tasks")
    print("• No extra top margins")
    print("• No extra left margins")
    print("• Visual consistency with task content")
    print("• Correct empty column text content")
    print("=" * 50)
    
    tests = [
        test_empty_column_positioning,
        test_empty_vs_task_alignment,
        test_no_extra_margins,
        test_visual_consistency,
        test_empty_column_text_content
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
        print("🎉 All empty column positioning tests passed!")
        print("✅ Empty column text is properly aligned!")
        print()
        print("🎯 Features verified:")
        print("• Empty text positioned at same level as tasks")
        print("• No unwanted top margins")
        print("• No unwanted left margins") 
        print("• Visual consistency across columns")
        print("• Correct text content displayed")
        return True
    else:
        print("❌ Some empty column positioning tests failed.")
        print("💡 Check the empty column display functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)