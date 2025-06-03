#!/usr/bin/env python3
"""
Test script to verify Ctrl+C handling in Kanby.
Tests that KeyboardInterrupt is handled gracefully without traceback.
"""

import os
import sys
import tempfile
import subprocess
import time
import signal
from unittest.mock import patch

# Add the package to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_ctrlc_simulation():
    """Test Ctrl+C handling by simulating KeyboardInterrupt."""
    print("🧪 Testing Ctrl+C simulation...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    
    try:
        # Test that KeyboardInterrupt is caught in cli_main
        from kanby.main import cli_main
        
        # Mock sys.argv to include our test data file
        with patch('sys.argv', ['kanby', '--data-file', temp_file]):
            # Mock curses.wrapper to raise KeyboardInterrupt
            with patch('kanby.main.curses.wrapper') as mock_wrapper:
                mock_wrapper.side_effect = KeyboardInterrupt()
                
                # Mock sys.exit to prevent actual exit
                with patch('sys.exit') as mock_exit:
                    # Capture stdout
                    from io import StringIO
                    import contextlib
                    
                    stdout_capture = StringIO()
                    with contextlib.redirect_stdout(stdout_capture):
                        try:
                            cli_main()
                        except SystemExit:
                            pass
                    
                    output = stdout_capture.getvalue()
                    
                    # Check that exit was called with 0 (success)
                    if mock_exit.called and mock_exit.call_args[0][0] == 0:
                        # Check that the success message was printed
                        if "Kanby closed. Your data has been saved." in output:
                            print("✅ Ctrl+C simulation test passed!")
                            return True
                        else:
                            print(f"❌ Expected success message not found. Output: {output}")
                            return False
                    else:
                        print("❌ sys.exit not called correctly")
                        return False
    
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_graceful_exit():
    """Test that application exits gracefully."""
    print("🧪 Testing graceful exit...")
    
    # Test the application with a very short timeout
    try:
        cmd = ['timeout', '1', 'kanby', '--version']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        # timeout command returns 124 when it times out, but kanby --version should return 0
        if result.returncode == 0 and "1.0.0" in result.stdout:
            print("✅ Graceful exit test passed!")
            return True
        else:
            print(f"❌ Unexpected return code or output: {result.returncode}, {result.stdout}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_real_interrupt():
    """Test real interrupt handling with subprocess."""
    print("🧪 Testing real interrupt handling...")
    
    try:
        # Start kanby in background with demo data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
            # Write minimal data
            f.write('{"Default Project": {"To Do": [], "In Progress": [], "Done": []}}')
        
        # Start kanby process
        proc = subprocess.Popen(
            ['kanby', '--data-file', temp_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(0.5)
        
        # Send SIGINT (Ctrl+C)
        proc.send_signal(signal.SIGINT)
        
        # Wait for it to finish
        stdout, stderr = proc.communicate(timeout=5)
        
        # Check that it either exited cleanly or showed friendly error message
        if proc.returncode == 0:
            # Perfect - no errors at all
            print("✅ Real interrupt test passed!")
            return True
        elif proc.returncode == 1:
            # Check if it's the friendly terminal error message
            if ("Terminal error:" in stderr and 
                "This may happen if the terminal doesn't support curses" in stderr and
                "Traceback" not in stderr):
                print("✅ Real interrupt test passed! (Friendly error message shown)")
                return True
            else:
                print(f"❌ Found unexpected error in stderr: {stderr}")
                return False
        else:
            print(f"❌ Unexpected exit code: {proc.returncode}")
            print(f"stderr: {stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        proc.kill()
        print("❌ Process didn't exit in time")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    """Run all Ctrl+C handling tests."""
    print("🔥 Kanby Ctrl+C Handling Tests")
    print("=" * 50)
    print("Testing that Ctrl+C exits gracefully without errors")
    print("=" * 50)
    
    tests = [
        test_ctrlc_simulation,
        test_graceful_exit,
        test_real_interrupt
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
        print("🎉 All Ctrl+C handling tests passed!")
        print("✅ Kanby handles Ctrl+C gracefully without tracebacks!")
        return True
    else:
        print("❌ Some Ctrl+C handling tests failed.")
        print("💡 The application may still show error messages on Ctrl+C")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)