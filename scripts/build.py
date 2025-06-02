#!/usr/bin/env python3
"""
Build script for Kanby package.
Handles building, testing, and publishing the package.
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"💻 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    
    return result

def clean():
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    # Directories to clean
    dirs_to_clean = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        "kanby/__pycache__"
    ]
    
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"  Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"  Removing file: {path}")
                path.unlink()
    
    print("✅ Clean complete!")

def test():
    """Run tests."""
    print("🧪 Running tests...")
    
    if Path("test_kanby.py").exists():
        result = run_command("python test_kanby.py", check=False)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Tests failed!")
            return False
    else:
        print("⚠️  No tests found. Creating basic import test...")
        # Basic import test
        try:
            import kanby
            print("✅ Package imports successfully!")
            return True
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            return False

def lint():
    """Run basic code quality checks."""
    print("🔍 Running code quality checks...")
    
    # Check for basic Python syntax
    python_files = list(Path("kanby").glob("*.py"))
    
    for py_file in python_files:
        result = run_command(f"python -m py_compile {py_file}", check=False)
        if result.returncode != 0:
            print(f"❌ Syntax error in {py_file}")
            return False
    
    print("✅ Code quality checks passed!")
    return True

def build():
    """Build the package."""
    print("📦 Building package...")
    
    # Install build dependencies
    run_command("python -m pip install --upgrade build")
    
    # Build the package
    run_command("python -m build")
    
    print("✅ Package built successfully!")
    
    # Show build artifacts
    if Path("dist").exists():
        print("\n📋 Build artifacts:")
        for artifact in Path("dist").iterdir():
            print(f"  {artifact.name}")

def install_dev():
    """Install the package in development mode."""
    print("⚙️  Installing in development mode...")
    run_command("python -m pip install -e .")
    print("✅ Development installation complete!")

def check_package():
    """Check the built package."""
    print("🔍 Checking package...")
    
    # Install check dependencies
    run_command("python -m pip install --upgrade twine", check=False)
    
    # Check the package
    if Path("dist").exists():
        run_command("python -m twine check dist/*")
        print("✅ Package check passed!")
    else:
        print("❌ No dist directory found. Run build first.")
        return False

def publish_test():
    """Publish to test PyPI."""
    print("🚀 Publishing to test PyPI...")
    
    if not Path("dist").exists():
        print("❌ No dist directory found. Run build first.")
        return False
    
    run_command("python -m twine upload --repository testpypi dist/*")
    print("✅ Published to test PyPI!")

def publish():
    """Publish to PyPI."""
    print("🚀 Publishing to PyPI...")
    
    if not Path("dist").exists():
        print("❌ No dist directory found. Run build first.")
        return False
    
    # Confirm publication
    response = input("Are you sure you want to publish to PyPI? (y/N): ")
    if response.lower() != 'y':
        print("❌ Publication cancelled.")
        return False
    
    run_command("python -m twine upload dist/*")
    print("✅ Published to PyPI!")

def setup_dev():
    """Set up development environment."""
    print("🛠️  Setting up development environment...")
    
    # Install development dependencies
    dev_deps = [
        "build",
        "twine", 
        "pytest",
        "black",
        "flake8"
    ]
    
    for dep in dev_deps:
        run_command(f"python -m pip install {dep}", check=False)
    
    # Install in development mode
    install_dev()
    
    print("✅ Development environment ready!")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build script for Kanby")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Commands
    subparsers.add_parser("clean", help="Clean build artifacts")
    subparsers.add_parser("test", help="Run tests")
    subparsers.add_parser("lint", help="Run code quality checks")
    subparsers.add_parser("build", help="Build the package")
    subparsers.add_parser("check", help="Check the built package")
    subparsers.add_parser("install-dev", help="Install in development mode")
    subparsers.add_parser("setup-dev", help="Set up development environment")
    subparsers.add_parser("publish-test", help="Publish to test PyPI")
    subparsers.add_parser("publish", help="Publish to PyPI")
    subparsers.add_parser("all", help="Run clean, test, lint, and build")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print(f"🔥 Kanby Build Script")
    print(f"📁 Working directory: {PROJECT_ROOT}")
    print("=" * 50)
    
    try:
        if args.command == "clean":
            clean()
        elif args.command == "test":
            if not test():
                sys.exit(1)
        elif args.command == "lint":
            if not lint():
                sys.exit(1)
        elif args.command == "build":
            build()
        elif args.command == "check":
            check_package()
        elif args.command == "install-dev":
            install_dev()
        elif args.command == "setup-dev":
            setup_dev()
        elif args.command == "publish-test":
            publish_test()
        elif args.command == "publish":
            publish()
        elif args.command == "all":
            clean()
            if not test():
                sys.exit(1)
            if not lint():
                sys.exit(1)
            build()
            check_package()
        
        print("\n🎉 Command completed successfully!")
        
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()