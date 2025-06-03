#!/usr/bin/env python3
"""
Test script for selected task highlighting overflow fix.
Tests that selected task highlighting doesn't overflow into adjacent columns.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import draw_board, DEFAULT_COLUMNS, DEFAULT_COLUMN_WIDTH

def test_selected_task_no_overflow():
    """Test that selected tasks don't overflow into next column."""
    print("🧪 Testing selected task overflow fix...")
    
    test_data = {
        "To Do": [{"id": "1", "title": "Selected task", "priority": "High"}],
        "In Progress": [{"id": "2", "title": "Another task", "priority": "Mid"}],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    # Draw with first task selected (column 0, task 0)
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Find calls that might be selection highlighting
    calls = mock_stdscr.addstr.call_args_list
    
    # Look for calls with selection-related content
    selection_calls = []
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[H] Selected task" in text:
                selection_calls.append(call)
    
    if selection_calls:
        # Check positioning and width
        call = selection_calls[0]
        y_pos = call[0][0]
        x_pos = call[0][1]
        text = call[0][2]
        
        # With +1 left margin, x_pos should be 1
        # Text length should not exceed col_width - 1
        expected_x = 1
        max_text_length = DEFAULT_COLUMN_WIDTH - 1
        
        if x_pos == expected_x and len(text) <= max_text_length:
            print("✅ Selected task overflow fix test passed!")
            return True
        else:
            print(f"❌ Selection positioning issue: x={x_pos}, text_len={len(text)}")
            return False
    else:
        print("❌ Could not find selection calls")
        return False

def test_selection_width_calculation():
    """Test that selection highlighting width is calculated correctly."""
    print("🧪 Testing selection width calculation...")
    
    # Test with long task title that would cause overflow
    long_title = "This is a very long task title that might cause overflow issues"
    test_data = {
        "To Do": [{"id": "1", "title": long_title, "priority": "High"}],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    long_task_calls = []
    
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[H]" in text and "very long" in text:
                long_task_calls.append(call)
    
    if long_task_calls:
        call = long_task_calls[0]
        text = call[0][2]
        
        # Text should be truncated to fit within column bounds
        # With +1 left margin, max width should be col_width - 1
        max_allowed_width = DEFAULT_COLUMN_WIDTH - 1
        
        if len(text) <= max_allowed_width:
            print("✅ Selection width calculation test passed!")
            return True
        else:
            print(f"❌ Text too long: {len(text)} > {max_allowed_width}")
            return False
    else:
        print("❌ Could not find long task calls")
        return False

def test_multi_column_selection():
    """Test selection highlighting in different columns."""
    print("🧪 Testing multi-column selection...")
    
    test_data = {
        "To Do": [{"id": "1", "title": "First task", "priority": "High"}],
        "In Progress": [{"id": "2", "title": "Second task", "priority": "Mid"}],
        "Done": [{"id": "3", "title": "Third task", "priority": "Low"}]
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 120)  # Wider screen for 3 columns
    
    # Test selection in middle column (In Progress)
    draw_board(mock_stdscr, test_data, 1, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    middle_column_calls = []
    
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[M] Second task" in text:
                middle_column_calls.append(call)
    
    if middle_column_calls:
        call = middle_column_calls[0]
        x_pos = call[0][1]
        text = call[0][2]
        
        # Should be positioned in middle column with proper margin
        # Middle column starts around x=31, so with margin should be ~32
        expected_range = (30, 35)  # Allow some variance
        max_text_length = DEFAULT_COLUMN_WIDTH - 1
        
        if (expected_range[0] <= x_pos <= expected_range[1] and 
            len(text) <= max_text_length):
            print("✅ Multi-column selection test passed!")
            return True
        else:
            print(f"❌ Middle column positioning issue: x={x_pos}, text_len={len(text)}")
            return False
    else:
        print("❌ Could not find middle column selection")
        return False

def test_edge_case_selection():
    """Test selection highlighting edge cases."""
    print("🧪 Testing selection edge cases...")
    
    # Test with very short and very long task names
    test_data = {
        "To Do": [
            {"id": "1", "title": "A", "priority": "High"},  # Very short
            {"id": "2", "title": "Very long task name that definitely exceeds normal limits", "priority": "Mid"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    # Test with short task selected
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    short_task_calls = []
    
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[H] A" in text:
                short_task_calls.append(call)
    
    # Test with long task selected  
    draw_board(mock_stdscr, test_data, 0, 1, "Test Project", True)
    
    calls = mock_stdscr.addstr.call_args_list
    long_task_calls = []
    
    for call in calls:
        if len(call[0]) >= 3:
            text = str(call[0][2])
            if "[M]" in text and "Very long" in text:
                long_task_calls.append(call)
    
    # Check both cases
    short_ok = len(short_task_calls) > 0
    long_ok = len(long_task_calls) > 0
    
    if short_ok and long_ok:
        # Verify long task is properly truncated
        long_text = long_task_calls[0][0][2]
        max_width = DEFAULT_COLUMN_WIDTH - 1
        
        if len(long_text) <= max_width:
            print("✅ Selection edge cases test passed!")
            return True
        else:
            print(f"❌ Long task not truncated: {len(long_text)} > {max_width}")
            return False
    else:
        print("❌ Could not find edge case selections")
        return False

def test_highlighting_consistency():
    """Test that highlighting is consistent across scenarios."""
    print("🧪 Testing highlighting consistency...")
    
    test_data = {
        "To Do": [
            {"id": "1", "title": "Task one", "priority": "High"},
            {"id": "2", "title": "Task two", "priority": "Mid"},
            {"id": "3", "title": "Task three", "priority": "Low"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    # Test selection on different tasks
    selection_positions = []
    
    for task_idx in range(3):
        draw_board(mock_stdscr, test_data, 0, task_idx, "Test Project", True)
        calls = mock_stdscr.addstr.call_args_list
        
        for call in calls:
            if len(call[0]) >= 3:
                text = str(call[0][2])
                # Look for the selected task (should have priority marker)
                if ("[H]" in text and task_idx == 0) or \
                   ("[M]" in text and task_idx == 1) or \
                   ("[L]" in text and task_idx == 2):
                    x_pos = call[0][1]
                    text_len = len(text)
                    selection_positions.append((x_pos, text_len))
                    break
    
    # All selections should have same x position (with margin)
    # and reasonable text lengths
    if len(selection_positions) >= 2:
        x_positions = [pos[0] for pos in selection_positions]
        text_lengths = [pos[1] for pos in selection_positions]
        
        # All x positions should be the same (consistent margin)
        x_consistent = len(set(x_positions)) == 1
        
        # All text lengths should be reasonable
        max_width = DEFAULT_COLUMN_WIDTH - 1
        lengths_ok = all(length <= max_width for length in text_lengths)
        
        if x_consistent and lengths_ok:
            print("✅ Highlighting consistency test passed!")
            return True
        else:
            print(f"❌ Inconsistent highlighting: x_positions={x_positions}, lengths={text_lengths}")
            return False
    else:
        print("❌ Could not find enough selection positions")
        return False

def main():
    """Run all selection overflow fix tests."""
    print("🔥 Kanby Selection Overflow Fix Tests")
    print("=" * 45)
    print("Testing:")
    print("• Selected tasks don't overflow into next column")
    print("• Selection width calculated correctly")
    print("• Multi-column selection positioning")
    print("• Edge cases (short/long task names)")
    print("• Highlighting consistency across scenarios")
    print("=" * 45)
    
    tests = [
        test_selected_task_no_overflow,
        test_selection_width_calculation,
        test_multi_column_selection,
        test_edge_case_selection,
        test_highlighting_consistency
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
    
    print("=" * 45)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All selection overflow fix tests passed!")
        print("✅ Selected task highlighting properly contained!")
        print()
        print("🎯 Features verified:")
        print("• No overflow into adjacent columns")
        print("• Proper width calculation with left margin")
        print("• Consistent highlighting across columns")
        print("• Edge cases handled correctly")
        print("• Visual consistency maintained")
        return True
    else:
        print("❌ Some selection overflow fix tests failed.")
        print("💡 Check the selection highlighting implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)