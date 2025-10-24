#!/usr/bin/env python3
"""
Installation test script for HubSpot Segmentation Explorer.
Run this to verify all dependencies are correctly installed.
"""

import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...\n")
    
    packages = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'plotly': 'Plotly',
        'openpyxl': 'OpenPyXL',
        'xlsxwriter': 'XlsxWriter',
        'dateutil': 'python-dateutil',
    }
    
    failed = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name} - {str(e)}")
            failed.append(name)
    
    print()
    
    if failed:
        print(f"❌ Failed to import: {', '.join(failed)}")
        print("\nTo fix, run:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed!")
        return True


def test_app_structure():
    """Test that the app structure is correct."""
    print("\nTesting app structure...\n")
    
    from pathlib import Path
    
    base_dir = Path(__file__).parent
    
    required_files = [
        'app/app.py',
        'app/utils/__init__.py',
        'app/utils/load.py',
        'app/utils/features.py',
        'app/utils/profiling.py',
        'app/utils/cluster1.py',
        'app/utils/cluster2.py',
        'app/utils/cluster3.py',
        'app/utils/charts.py',
        'app/utils/exports.py',
        'app/pages/01_Overview.py',
        'app/pages/02_Cluster1_Social.py',
        'app/pages/03_Cluster2_Geo.py',
        'app/pages/04_Cluster3_APREU.py',
        'app/pages/05_Lookups.py',
        'app/pages/06_Exports.py',
        'requirements.txt',
        '.streamlit/config.toml',
    ]
    
    missing = []
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            missing.append(file_path)
    
    print()
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    else:
        print("✅ All required files are present!")
        return True


def test_utils_import():
    """Test that utils modules can be imported."""
    print("\nTesting utils modules...\n")
    
    sys.path.insert(0, str(Path(__file__).parent / 'app'))
    
    modules = [
        'utils.load',
        'utils.features',
        'utils.profiling',
        'utils.cluster1',
        'utils.cluster2',
        'utils.cluster3',
        'utils.charts',
        'utils.exports',
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module} - {str(e)}")
            failed.append(module)
    
    print()
    
    if failed:
        print(f"❌ Failed to import modules: {', '.join(failed)}")
        return False
    else:
        print("✅ All utils modules import successfully!")
        return True


def main():
    """Run all tests."""
    from pathlib import Path
    
    print("="*60)
    print("HubSpot Segmentation Explorer - Installation Test")
    print("="*60)
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print()
    
    if sys.version_info < (3, 11):
        print("⚠️  Warning: Python 3.11+ recommended")
        print()
    
    # Run tests
    test1 = test_imports()
    test2 = test_app_structure()
    test3 = test_utils_import()
    
    print("="*60)
    
    if test1 and test2 and test3:
        print("🎉 SUCCESS! Installation is complete and working.")
        print()
        print("To start the app, run:")
        print("  streamlit run app/app.py")
        return 0
    else:
        print("❌ FAILED! Please fix the issues above.")
        return 1


if __name__ == '__main__':
    from pathlib import Path
    
    sys.exit(main())

