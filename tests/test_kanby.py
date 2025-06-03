#!/usr/bin/env python3
"""
Simple test script for Kanby package functionality.
Tests core functions without requiring curses interface.
"""

import os
import json
import tempfile
import sys
import unittest
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from kanby.main import generate_id, load_data, save_data, DEFAULT_COLUMNS, DEFAULT_PROJECT_NAME, is_key_pressed


class TestKanby(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary file."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.temp_dir, 'test_kanban.json')
        
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        os.rmdir(self.temp_dir)
    
    def test_generate_id(self):
        """Test ID generation."""
        id1 = generate_id()
        id2 = generate_id()
        
        # IDs should be strings
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        
        # IDs should be 8 characters long
        self.assertEqual(len(id1), 8)
        self.assertEqual(len(id2), 8)
        
        # IDs should be unique
        self.assertNotEqual(id1, id2)
    
    @patch('kanby.main.DATA_FILE')
    def test_load_data_empty_file(self, mock_data_file):
        """Test loading data when file doesn't exist."""
        mock_data_file.return_value = self.test_data_file
        
        with patch('kanby.main.DATA_FILE', self.test_data_file):
            data = load_data()
        
        # Should return default structure
        self.assertIsInstance(data, dict)
        self.assertIn(DEFAULT_PROJECT_NAME, data)
        
        for col in DEFAULT_COLUMNS:
            self.assertIn(col, data[DEFAULT_PROJECT_NAME])
            self.assertEqual(data[DEFAULT_PROJECT_NAME][col], [])
    
    @patch('kanby.main.DATA_FILE')
    def test_save_and_load_data(self, mock_data_file):
        """Test saving and loading data."""
        mock_data_file.return_value = self.test_data_file
        
        # Create test data
        test_data = {
            "Test Project": {
                "To Do": [
                    {"id": "test123", "title": "Test Task", "priority": "High"}
                ],
                "In Progress": [],
                "Done": []
            }
        }
        
        with patch('kanby.main.DATA_FILE', self.test_data_file):
            save_data(test_data)
            loaded_data = load_data()
        
        # Verify data was saved and loaded correctly
        self.assertEqual(loaded_data, test_data)
    
    @patch('kanby.main.DATA_FILE')
    def test_load_data_migration(self, mock_data_file):
        """Test data migration from old format."""
        mock_data_file.return_value = self.test_data_file
        
        # Create old format data
        old_data = {
            "To Do": [{"title": "Old Task"}],
            "In Progress": [],
            "Done": []
        }
        
        # Save old format
        with open(self.test_data_file, 'w') as f:
            json.dump(old_data, f)
        
        with patch('kanby.main.DATA_FILE', self.test_data_file):
            loaded_data = load_data()
        
        # Should be migrated to new format
        self.assertIn(DEFAULT_PROJECT_NAME, loaded_data)
        self.assertIn("To Do", loaded_data[DEFAULT_PROJECT_NAME])
        
        # Check that task was migrated and has required fields
        task = loaded_data[DEFAULT_PROJECT_NAME]["To Do"][0]
        self.assertEqual(task["title"], "Old Task")
        self.assertIn("id", task)
        self.assertIn("priority", task)
    
    def test_package_import(self):
        """Test that the package can be imported correctly."""
        import kanby
        
        # Check that package has expected attributes
        self.assertTrue(hasattr(kanby, '__version__'))
        self.assertTrue(hasattr(kanby, 'cli_main'))
        self.assertTrue(hasattr(kanby, '__description__'))
    
    def test_cli_main_function_exists(self):
        """Test that cli_main function exists and is callable."""
        from kanby.main import cli_main
        
        self.assertTrue(callable(cli_main))
    
    def test_keyboard_input_detection(self):
        """Test that keyboard input detection works with different layouts."""
        # Test basic ASCII character detection
        self.assertTrue(is_key_pressed(ord('q'), 'q'))
        self.assertTrue(is_key_pressed(ord('Q'), 'q'))
        self.assertTrue(is_key_pressed(ord('a'), 'a'))
        self.assertTrue(is_key_pressed(ord('A'), 'a'))
        
        # Test case insensitivity
        self.assertTrue(is_key_pressed(ord('p'), 'P'))
        self.assertTrue(is_key_pressed(ord('P'), 'p'))
        
        # Test non-matching keys
        self.assertFalse(is_key_pressed(ord('x'), 'q'))
        self.assertFalse(is_key_pressed(ord('1'), 'a'))
        
        # Test that non-ASCII characters don't match
        self.assertFalse(is_key_pressed(200, 'a'))  # High-bit char should not match A
        self.assertFalse(is_key_pressed(250, 'm'))  # High-bit char should not match M
        self.assertFalse(is_key_pressed(180, 'p'))  # High-bit char should not match P
        self.assertFalse(is_key_pressed(160, 'q'))  # High-bit char should not match Q
        self.assertFalse(is_key_pressed(220, 'd'))  # High-bit char should not match D
        self.assertFalse(is_key_pressed(240, 'e'))  # High-bit char should not match E
        self.assertFalse(is_key_pressed(200, 'x'))  # High-bit char should not match X
        self.assertFalse(is_key_pressed(200, 'z'))  # High-bit char should not match Z
        
        # Test invalid inputs
        self.assertFalse(is_key_pressed(ord('q'), ''))
        self.assertFalse(is_key_pressed(ord('q'), 'qq'))
        self.assertFalse(is_key_pressed(ord('q'), None))


def run_tests():
    """Run all tests and display results."""
    print("🧪 Running Kanby Tests...")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestKanby)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! Kanby is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)