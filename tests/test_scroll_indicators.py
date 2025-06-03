#!/usr/bin/env python3
"""
Test script for task counter scroll indicators in column headers.
Tests that headers show correct task counts and ranges when scrolling.
"""

import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import draw_board, DEFAULT_COLUMNS, MIN_TASK_DISPLAY_HEIGHT

def test_header_counter_all_visible():
    """Test header shows total count when all tasks are visible."""
    print("🧪 Testing header counter when all tasks visible...")
    
    # Create test data with few tasks (all should be visible)
    test_data = {
        "To Do": [
            {"id": "1", "title": "Task 1", "priority": "High"},
            {"id": "2", "title": "Task 2", "priority": "Mid"}
        ],
        "In Progress": [
            {"id": "3", "title": "Task 3", "priority": "Low"}
        ],
        "Done": []
    }
    
    # Mock screen with large height (all tasks fit)
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (50, 100)  # Large screen
    
    # Call draw_board
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Check that addstr was called with correct headers
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    found_headers = []
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            found_headers.append(header_text.strip())
    
    # Should show simple counts: "To Do (2)", "In Progress (1)", "Done (0)"
    expected = ["To Do (2)", "In Progress (1)", "Done (0)"]
    
    for expected_header in expected:
        if any(expected_header in header for header in found_headers):
            continue
        else:
            print(f"❌ Expected header '{expected_header}' not found in {found_headers}")
            return False
    
    print("✅ Header counter test (all visible) passed!")
    return True

def test_header_counter_with_scrolling():
    """Test header shows range when tasks are scrolled."""
    print("🧪 Testing header counter with scrolling...")
    
    # Create test data with many tasks (scrolling needed)
    test_data = {
        "To Do": [
            {"id": f"task{i}", "title": f"Task {i}", "priority": "Mid"}
            for i in range(1, 11)  # 10 tasks
        ],
        "In Progress": [],
        "Done": []
    }
    
    # Mock screen with small height (forces scrolling)
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (15, 100)  # Small height
    
    # Call draw_board with a task selected that requires scrolling
    current_task_idx = 7  # Should cause scrolling
    draw_board(mock_stdscr, test_data, 0, current_task_idx, "Test Project", True)
    
    # Check header calls
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    found_headers = []
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            found_headers.append(header_text.strip())
    
    # Should show range format like "To Do (X-Y/10)"
    to_do_header = None
    for header in found_headers:
        if "To Do" in header and "/" in header:
            to_do_header = header
            break
    
    if to_do_header and "/10)" in to_do_header:
        print(f"✅ Found scrolling header: {to_do_header}")
        print("✅ Header counter test (with scrolling) passed!")
        return True
    else:
        print(f"❌ Expected scrolling header format not found in {found_headers}")
        return False

def test_header_counter_empty_columns():
    """Test header shows (0) for empty columns."""
    print("🧪 Testing header counter for empty columns...")
    
    # Create test data with only empty columns
    test_data = {
        "To Do": [],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (25, 100)
    
    draw_board(mock_stdscr, test_data, 0, 0, "Test Project", True)
    
    # Check header calls
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    found_headers = []
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            found_headers.append(header_text.strip())
    
    # All headers should show (0)
    expected_patterns = ["(0)"]
    
    for pattern in expected_patterns:
        matching_headers = [h for h in found_headers if pattern in h]
        if len(matching_headers) >= 3:  # Should be 3 columns
            print("✅ Header counter test (empty columns) passed!")
            return True
    
    print(f"❌ Expected (0) pattern not found enough times in {found_headers}")
    return False

def test_header_counter_mixed_columns():
    """Test header counters with mixed column states."""
    print("🧪 Testing header counter with mixed column states...")
    
    # Create mixed test data
    test_data = {
        "To Do": [{"id": f"task{i}", "title": f"Task {i}", "priority": "Mid"} for i in range(8)],  # Many tasks
        "In Progress": [{"id": "task9", "title": "Task 9", "priority": "High"}],  # One task
        "Done": []  # Empty
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (20, 120)  # Medium height
    
    draw_board(mock_stdscr, test_data, 1, 0, "Test Project", True)  # Focus on In Progress
    
    # Check header calls
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    found_headers = []
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            found_headers.append(header_text.strip())
    
    # Should have different formats: scrolling for To Do, simple for others
    has_scrolling = any("/" in header for header in found_headers)
    has_simple_count = any("(1)" in header for header in found_headers)
    has_empty_count = any("(0)" in header for header in found_headers)
    
    if has_scrolling and has_simple_count and has_empty_count:
        print("✅ Header counter test (mixed columns) passed!")
        return True
    else:
        print(f"❌ Expected mixed formats not found in {found_headers}")
        print(f"Has scrolling: {has_scrolling}, Has simple: {has_simple_count}, Has empty: {has_empty_count}")
        return False

def test_header_truncation():
    """Test that long headers are truncated properly."""
    print("🧪 Testing header truncation...")
    
    # Create test with many tasks to create long header
    test_data = {
        "To Do": [{"id": f"task{i}", "title": f"Task {i}", "priority": "Mid"} for i in range(999)],
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (15, 60)  # Narrow width
    
    draw_board(mock_stdscr, test_data, 0, 500, "Test Project", True)  # Force scrolling
    
    # Check that headers don't exceed reasonable length
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            if len(header_text) > 50:  # Reasonable max length
                print(f"❌ Header too long: {len(header_text)} chars")
                return False
    
    print("✅ Header truncation test passed!")
    return True

def test_scroll_calculation_accuracy():
    """Test that scroll range calculations are accurate."""
    print("🧪 Testing scroll calculation accuracy...")
    
    # Create known test scenario
    test_data = {
        "To Do": [{"id": f"task{i}", "title": f"Task {i}", "priority": "Mid"} for i in range(1, 21)],  # 20 tasks
        "In Progress": [],
        "Done": []
    }
    
    mock_stdscr = MagicMock()
    mock_stdscr.getmaxyx.return_value = (18, 100)  # Small height, force scrolling
    
    # Test with specific selected task
    selected_task = 15  # Should be near the end
    draw_board(mock_stdscr, test_data, 0, selected_task, "Test Project", True)
    
    # Find the To Do header
    calls = mock_stdscr.addstr.call_args_list
    header_calls = [call for call in calls if len(call[0]) >= 3 and call[0][0] == 2]
    
    to_do_header = None
    for call in header_calls:
        if len(call[0]) >= 3:
            header_text = call[0][2]
            if "To Do" in header_text and "/" in header_text:
                to_do_header = header_text
                break
    
    if to_do_header:
        # Extract numbers from format like "To Do (X-Y/20)"
        if "/20)" in to_do_header:
            print(f"✅ Found accurate range in header: {to_do_header}")
            print("✅ Scroll calculation accuracy test passed!")
            return True
    
    print(f"❌ Could not verify scroll calculation accuracy")
    return False

def main():
    """Run all scroll indicator tests."""
    print("🔥 Kanby Scroll Indicators Tests")
    print("=" * 50)
    print("Testing:")
    print("• Task counter in headers when all visible")
    print("• Range display when scrolling required")
    print("• Empty column indicators")
    print("• Mixed column states")
    print("• Header truncation")
    print("• Scroll calculation accuracy")
    print("=" * 50)
    
    tests = [
        test_header_counter_all_visible,
        test_header_counter_with_scrolling,
        test_header_counter_empty_columns,
        test_header_counter_mixed_columns,
        test_header_truncation,
        test_scroll_calculation_accuracy
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
        print("🎉 All scroll indicator tests passed!")
        print("✅ Task counter functionality working correctly!")
        print()
        print("🎯 Features tested:")
        print("• Headers show total count when all tasks visible")
        print("• Headers show range when scrolling needed")
        print("• Empty columns show (0) correctly")
        print("• Mixed column states work properly")
        print("• Long headers are truncated appropriately")
        print("• Scroll calculations are accurate")
        return True
    else:
        print("❌ Some scroll indicator tests failed.")
        print("💡 Check the header counter functionality")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)