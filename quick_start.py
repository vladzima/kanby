#!/usr/bin/env python3
"""
Quick start script for Kanby development.
This script helps you get up and running quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the Kanby banner."""
    banner = """
🔥 KANBY - Quick Start Script
═══════════════════════════════════════════════════════════
Your Beautiful Terminal Kanban Board - Development Setup
═══════════════════════════════════════════════════════════
"""
    print(banner)

def check_python():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.7+")
        return False

def run_command(cmd, description):
    """Run a command with nice output."""
    print(f"⚙️  {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def install_package():
    """Install the package in development mode."""
    print("\n📦 Installing Kanby in development mode...")
    return run_command("pip install -e .", "Installing package")

def run_tests():
    """Run basic tests."""
    print("\n🧪 Running tests...")
    if Path("test_kanby.py").exists():
        return run_command("python test_kanby.py", "Running tests")
    else:
        print("⚠️  No test file found, skipping tests")
        return True

def demo_run():
    """Show how to run the application."""
    print("\n🎯 Demo Instructions:")
    print("   To run Kanby:")
    print("   → python -m kanby.main")
    print("   → Or: kanby (after installation)")
    print("")
    print("   Keyboard controls:")
    print("   → ← → : Navigate columns")
    print("   → ↑ ↓ : Navigate tasks")
    print("   → a   : Add task")
    print("   → e   : Edit task")
    print("   → m   : Move task")
    print("   → p   : Manage projects")
    print("   → q   : Quit")

def check_requirements():
    """Check if all requirements are met."""
    print("\n🔍 Checking requirements...")
    
    # Check for curses (should be built-in on Unix systems)
    try:
        import curses
        print("✅ Curses library - Available")
    except ImportError:
        print("❌ Curses library - Not available (Windows users may need windows-curses)")
        return False
    
    # Check other standard libraries
    required_modules = ['json', 'os', 'time', 'uuid', 'argparse']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing")
            return False
    
    return True

def show_project_structure():
    """Show the project structure."""
    print("\n📁 Project Structure:")
    structure = """
    kanby/
    ├── kanby/
    │   ├── __init__.py    # Package initialization  
    │   └── main.py        # Main application code
    ├── scripts/
    │   └── build.py       # Build automation script
    ├── pyproject.toml     # Package configuration
    ├── README.md          # Documentation
    ├── LICENSE            # MIT License
    ├── test_kanby.py      # Basic tests
    └── quick_start.py     # This script
"""
    print(structure)

def main():
    """Main function."""
    print_banner()
    
    # Check Python version
    if not check_python():
        print("\n❌ Please upgrade to Python 3.7 or higher")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Missing requirements. Please install missing dependencies.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 SETUP PROCESS")
    print("="*60)
    
    # Install package
    if not install_package():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Tests failed, but you can still continue.")
    
    # Success message
    print("\n" + "="*60)
    print("🎉 SUCCESS! Kanby is ready to use!")
    print("="*60)
    
    # Show demo instructions
    demo_run()
    
    # Show project structure
    show_project_structure()
    
    print("\n📚 Next Steps:")
    print("   1. Try running: python -m kanby.main")
    print("   2. Check out the README.md for detailed docs")
    print("   3. Use scripts/build.py for development tasks")
    print("   4. Have fun organizing your tasks! 🎯")
    
    print("💡 Tips:")
    print("   → Your data is saved in kanby_data.json")
    print("   → Use --data-file to specify custom location")
    print("   → Press 'q' to quit the application")
    print("   → Use 'p' to manage multiple projects")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted. Run again anytime!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your Python installation and try again.")
        sys.exit(1)