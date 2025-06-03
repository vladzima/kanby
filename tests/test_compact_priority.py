#!/usr/bin/env python3
"""
Test script for compact priority format.
Tests that priorities are displayed as single letters on same line as title.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import draw_board, DEFAULT_COLUMNS, MIN_TASK_DISPLAY_HEIGHT

def test_priority_abbreviation():
    """Test that priorities are correctly abbreviated to single letters."""
    print("🧪 Testing priority abbreviation...")
    
    test_data = {
        "To Do": [
            {"id": "1", "title": "High priority task", "priority": "High"},
            {"id": "2", "title": "Medium priority task", "priority": "Mid"},
            {"id": "3", "title": "Low priority task", "priority": "Low"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Check addstr calls for task content
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and isinstance(call[0][2], str)]
    
    found_formats = []
    for call in task_calls:
        text = call[0][2]
        if text.startswith('[') and ']' in text:
            found_formats.append(text)
    
    # Should find abbreviated formats
    expected_patterns = ["[H]", "[M]", "[L]"]
    for pattern in expected_patterns:
        if any(pattern in format_text for format_text in found_formats):
            continue
        else:
            print(f"❌ Expected pattern '{pattern}' not found in {found_formats}")
            return False
    
    print("✅ Priority abbreviation test passed!")
    return True

def test_single_line_format():
    """Test that priority and title are on the same line."""
    print("🧪 Testing single line format...")
    
    test_data = {
        "To Do": [
            {"id": "1", "title": "Example task", "priority": "High"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Find task-related calls
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and isinstance(call[0][2], str)]
    
    # Look for the combined format
    found_combined = False
    for call in task_calls:
        text = call[0][2]
        if "[H] Example task" in text:
            found_combined = True
            break
    
    if found_combined:
        print("✅ Single line format test passed!")
        return True
    else:
        print(f"❌ Combined format not found in calls")
        return False

def test_min_task_height():
    """Test that MIN_TASK_DISPLAY_HEIGHT is now 1."""
    print("🧪 Testing MIN_TASK_DISPLAY_HEIGHT...")
    
    if MIN_TASK_DISPLAY_HEIGHT == 1:
        print("✅ MIN_TASK_DISPLAY_HEIGHT test passed!")
        return True
    else:
        print(f"❌ Expected MIN_TASK_DISPLAY_HEIGHT=1, got {MIN_TASK_DISPLAY_HEIGHT}")
        return False

def test_title_truncation():
    """Test that long titles are properly truncated."""
    print("🧪 Testing title truncation...")
    
    long_title = "This is a very long task title that should be truncated when displayed"
    test_data = {
        "To Do": [
            {"id": "1", "title": long_title, "priority": "High"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 60)  # Narrow width
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Check that no single line is excessively long
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and isinstance(call[0][2], str)]
    
    max_reasonable_length = 50  # Should be within column width
    for call in task_calls:
        text = call[0][2]
        if "[H]" in text and len(text) > max_reasonable_length:
            print(f"❌ Text too long: {len(text)} chars")
            return False
    
    print("✅ Title truncation test passed!")
    return True

def test_all_priority_levels():
    """Test all priority levels display correctly."""
    print("🧪 Testing all priority levels...")
    
    test_data = {
        "To Do": [
            {"id": "1", "title": "Critical bug fix", "priority": "High"},
            {"id": "2", "title": "Feature request", "priority": "Mid"},
            {"id": "3", "title": "Documentation update", "priority": "Low"}
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Verify all priority abbreviations exist
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and isinstance(call[0][2], str)]
    
    all_text = " ".join([call[0][2] for call in task_calls])
    
    expected_combinations = [
        "[H] Critical bug fix",
        "[M] Feature request", 
        "[L] Documentation update"
    ]
    
    for expected in expected_combinations:
        if expected not in all_text:
            print(f"❌ Expected '{expected}' not found")
            return False
    
    print("✅ All priority levels test passed!")
    return True

def test_compact_space_usage():
    """Test that compact format uses less vertical space."""
    print("🧪 Testing compact space usage...")
    
    # Create data with many tasks
    test_data = {
        "To Do": [
            {"id": f"task{i}", "title": f"Task {i}", "priority": "High"}
            for i in range(10)
        ],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (20, 100)  # Limited height
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # With MIN_TASK_DISPLAY_HEIGHT = 1, more tasks should fit
    # Check that multiple tasks are being drawn
    calls = mock_stdscr.addstr.call_args_list
    task_calls = [call for call in calls if len(call[0]) >= 3 and isinstance(call[0][2], str)]
    
    task_count = len([call for call in task_calls if "[H] Task" in call[0][2]])
    
    if task_count >= 5:  # Should fit at least 5 tasks with compact format
        print(f"✅ Compact space usage test passed! ({task_count} tasks visible)")
        return True
    else:
        print(f"❌ Expected more tasks visible, only found {task_count}")
        return False

def main():
    """Run all compact priority format tests."""
    print("🔥 Kanby Compact Priority Format Tests")
    print("=" * 50)
    print("Testing:")
    print("• Priority abbreviation (High→H, Mid→M, Low→L)")
    print("• Single line format [X] Title")
    print("• Updated MIN_TASK_DISPLAY_HEIGHT") 
    print("• Title truncation handling")
    print("• All priority level display")
    print("• Improved space efficiency")
    print("=" * 50)
    
    tests = [
        test_priority_abbreviation,
        test_single_line_format,
        test_min_task_height,
        test_title_truncation,
        test_all_priority_levels,
        test_compact_space_usage
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
        print("🎉 All compact priority format tests passed!")
        print("✅ Priority display is now more space-efficient!")
        print()
        print("🎯 Features verified:")
        print("• Priorities abbreviated to single letters")
        print("• Priority and title on same line")
        print("• Reduced vertical space usage")
        print("• Proper truncation handling")
        print("• All priority levels working")
        print("• More tasks visible per screen")
        return True
    else:
        print("❌ Some compact priority format tests failed.")
        print("💡 Check the priority display functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)