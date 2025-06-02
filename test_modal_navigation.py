#!/usr/bin/env python3
"""
Test script specifically for modal arrow key navigation.
Tests that up/down arrows work properly in project management modal.
"""

import os
import sys
import tempfile
import json
from unittest.mock import MagicMock, patch, call

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from kanby.main import manage_projects_modal, DEFAULT_COLUMNS
import curses

def test_modal_arrow_navigation():
    """Test that arrow keys navigate properly in modal without closing."""
    print("🧪 Testing modal arrow key navigation...")
    
    # Create mock stdscr and modal_win
    mock_stdscr = MagicMock()
    mock_modal_win = MagicMock()
    
    # Mock terminal dimensions
    mock_stdscr.getmaxyx.return_value = (24, 80)
    
    # Create test projects data
    test_projects = {
        "Project A": {"To Do": [], "In Progress": [], "Done": []},
        "Project B": {"To Do": [], "In Progress": [], "Done": []},
        "Project C": {"To Do": [], "In Progress": [], "Done": []},
        "_meta": {"last_project": "Project A"}
    }
    
    # Simulate key sequence: DOWN, DOWN, UP, ENTER
    key_sequence = [
        curses.KEY_DOWN,  # Move from Project A to Project B
        curses.KEY_DOWN,  # Move from Project B to Project C  
        curses.KEY_UP,    # Move from Project C back to Project B
        ord('\n')         # Select Project B
    ]
    
    # Mock curses.newwin to return our mock modal window
    with patch('curses.newwin', return_value=mock_modal_win):
        # Mock the getch calls to return our key sequence
        mock_modal_win.getch.side_effect = key_sequence
        
        # Call the function
        result = manage_projects_modal(mock_stdscr, test_projects, "Project A", True)
        
        # Verify that keypad was enabled
        mock_modal_win.keypad.assert_called_once_with(True)
        
        # Verify that the function returned the correct project (Project B)
        if result == "Project B":
            print("✅ Modal arrow navigation test passed!")
            return True
        else:
            print(f"❌ Expected 'Project B', got '{result}'")
            return False

def test_modal_boundary_navigation():
    """Test navigation at boundaries (top/bottom of list)."""
    print("🧪 Testing modal boundary navigation...")
    
    mock_stdscr = MagicMock()
    mock_modal_win = MagicMock()
    mock_stdscr.getmaxyx.return_value = (24, 80)
    
    # Test with only 2 projects
    test_projects = {
        "First Project": {"To Do": [], "In Progress": [], "Done": []},
        "Second Project": {"To Do": [], "In Progress": [], "Done": []}
    }
    
    # Try to go up from first project (should stay at first)
    # Then go down to second, then try to go down again (should stay at second)
    key_sequence = [
        curses.KEY_UP,    # Try to go above first project
        curses.KEY_DOWN,  # Go to second project
        curses.KEY_DOWN,  # Try to go below second project
        ord('\n')         # Select (should be second project)
    ]
    
    with patch('curses.newwin', return_value=mock_modal_win):
        mock_modal_win.getch.side_effect = key_sequence
        
        result = manage_projects_modal(mock_stdscr, test_projects, "First Project", True)
        
        if result == "Second Project":
            print("✅ Modal boundary navigation test passed!")
            return True
        else:
            print(f"❌ Expected 'Second Project', got '{result}'")
            return False

def test_modal_does_not_close_on_arrows():
    """Test that modal doesn't close when arrow keys are pressed."""
    print("🧪 Testing modal doesn't close on arrow keys...")
    
    mock_stdscr = MagicMock()
    mock_modal_win = MagicMock()
    mock_stdscr.getmaxyx.return_value = (24, 80)
    
    test_projects = {
        "Project 1": {"To Do": [], "In Progress": [], "Done": []},
        "Project 2": {"To Do": [], "In Progress": [], "Done": []}
    }
    
    # Test multiple arrow presses followed by quit
    key_sequence = [
        curses.KEY_DOWN,
        curses.KEY_UP,
        curses.KEY_DOWN,
        curses.KEY_UP,
        ord('q')  # Quit to close modal
    ]
    
    with patch('curses.newwin', return_value=mock_modal_win):
        mock_modal_win.getch.side_effect = key_sequence
        
        result = manage_projects_modal(mock_stdscr, test_projects, "Project 1", True)
        
        # Should return the current project since we quit
        if result == "Project 1":
            print("✅ Modal arrow key handling test passed!")
            return True
        else:
            print(f"❌ Expected 'Project 1', got '{result}'")
            return False

def test_modal_keypad_enabled():
    """Test that modal window has keypad enabled."""
    print("🧪 Testing modal keypad enablement...")
    
    mock_stdscr = MagicMock()
    mock_modal_win = MagicMock()
    mock_stdscr.getmaxyx.return_value = (24, 80)
    
    test_projects = {
        "Test Project": {"To Do": [], "In Progress": [], "Done": []}
    }
    
    # Just quit immediately to test keypad call
    mock_modal_win.getch.return_value = ord('q')
    
    with patch('curses.newwin', return_value=mock_modal_win):
        manage_projects_modal(mock_stdscr, test_projects, "Test Project", True)
        
        # Verify keypad was enabled
        if mock_modal_win.keypad.called:
            if mock_modal_win.keypad.call_args == call(True):
                print("✅ Modal keypad enablement test passed!")
                return True
            else:
                print(f"❌ keypad called with wrong argument: {mock_modal_win.keypad.call_args}")
                return False
        else:
            print("❌ keypad was not called")
            return False

def test_single_project_navigation():
    """Test navigation with only one project."""
    print("🧪 Testing single project navigation...")
    
    mock_stdscr = MagicMock()
    mock_modal_win = MagicMock()
    mock_stdscr.getmaxyx.return_value = (24, 80)
    
    # Only one project
    test_projects = {
        "Only Project": {"To Do": [], "In Progress": [], "Done": []}
    }
    
    # Try arrows and then select
    key_sequence = [
        curses.KEY_UP,
        curses.KEY_DOWN,
        curses.KEY_UP,
        ord('\n')
    ]
    
    with patch('curses.newwin', return_value=mock_modal_win):
        mock_modal_win.getch.side_effect = key_sequence
        
        result = manage_projects_modal(mock_stdscr, test_projects, "Only Project", True)
        
        if result == "Only Project":
            print("✅ Single project navigation test passed!")
            return True
        else:
            print(f"❌ Expected 'Only Project', got '{result}'")
            return False

def main():
    """Run all modal navigation tests."""
    print("🔥 Kanby Modal Navigation Tests")
    print("=" * 50)
    print("Testing arrow key navigation in project management modal")
    print("=" * 50)
    
    tests = [
        test_modal_arrow_navigation,
        test_modal_boundary_navigation,
        test_modal_does_not_close_on_arrows,
        test_modal_keypad_enabled,
        test_single_project_navigation
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
        print("🎉 All modal navigation tests passed!")
        print("✅ Arrow keys should now work properly in project modal!")
        print()
        print("🎯 Key improvements:")
        print("• modal_win.keypad(True) enables arrow key capture")
        print("• Arrow keys navigate without closing modal")
        print("• Boundary handling works correctly")
        print("• Single project scenarios handled")
        return True
    else:
        print("❌ Some modal navigation tests failed.")
        print("💡 Arrow key navigation may still have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)