#!/usr/bin/env python3
"""
Build script for CO_O2_Analyser.

This script automates the build process for different distribution formats.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean build directories."""
    print("\n🧹 Cleaning build directories...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing {path}")
                path.unlink()

def build_source_distribution():
    """Build source distribution."""
    return run_command("python -m build --sdist", "Building source distribution")

def build_wheel():
    """Build wheel distribution."""
    return run_command("python -m build --wheel", "Building wheel distribution")

def build_all():
    """Build both source and wheel distributions."""
    return run_command("python -m build", "Building all distributions")

def create_standalone_executable():
    """Create standalone executable using PyInstaller."""
    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Create executable
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "CO_O2_Analyser",
        "--add-data", "src;co_o2_analyser",  # Windows
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "matplotlib.backends.backend_qt5agg",
        "--hidden-import", "matplotlib.backends.backend_qtagg",
        "main.py"
    ]
    
    return run_command(" ".join(pyinstaller_cmd), "Creating standalone executable")

def install_dependencies():
    """Install build dependencies."""
    dependencies = [
        "build",
        "wheel",
        "setuptools",
        "twine"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    return True

def main():
    """Main build function."""
    print("🚀 CO_O2_Analyser Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("\nUsage: python build.py [clean|deps|source|wheel|all|exe|full]")
        print("\nOptions:")
        print("  clean  - Clean build directories")
        print("  deps   - Install build dependencies")
        print("  source - Build source distribution only")
        print("  wheel  - Build wheel distribution only")
        print("  all    - Build both source and wheel distributions")
        print("  exe    - Create standalone executable")
        print("  full   - Clean, install deps, and build everything")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    success = True
    
    if command == "clean":
        clean_build_dirs()
        
    elif command == "deps":
        success = install_dependencies()
        
    elif command == "source":
        success = build_source_distribution()
        
    elif command == "wheel":
        success = build_wheel()
        
    elif command == "all":
        success = build_all()
        
    elif command == "exe":
        success = create_standalone_executable()
        
    elif command == "full":
        print("\n🔄 Running full build process...")
        clean_build_dirs()
        success = install_dependencies()
        if success:
            success = build_all()
        if success:
            success = create_standalone_executable()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    if success:
        print("\n🎉 Build process completed successfully!")
        print("\n📦 Generated files:")
        
        # List generated files
        if Path("dist").exists():
            for file in Path("dist").iterdir():
                print(f"  - {file}")
        
        if Path("build").exists():
            print(f"\n📁 Build directory: {Path('build').absolute()}")
        
        print("\n📋 Next steps:")
        print("1. Test the built package:")
        print("   pip install dist/co_o2_analyser-1.0.0-py3-none-any.whl")
        print("2. Upload to PyPI (if desired):")
        print("   twine upload dist/*")
        print("3. Test the standalone executable:")
        print("   ./dist/CO_O2_Analyser")
    else:
        print("\n❌ Build process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
