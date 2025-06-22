#!/usr/bin/env python3
"""
Test Runner Script

Convenience script to run backend tests from the backend directory.
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_name):
    """Run a specific test."""
    test_path = Path(__file__).parent / "tests" / f"{test_name}.py"
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False
    
    print(f"🧪 Running {test_name}...")
    try:
        result = subprocess.run([sys.executable, str(test_path)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_name}: {str(e)}")
        return False

def main():
    """Main function to run tests."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <test_name>")
        print("\nAvailable tests:")
        print("  test_db_queries    - Test database queries")
        print("  test_player_filter - Test player count filter")
        print("  test_performance   - Test API performance")
        print("  create_indexes     - Create database indexes")
        print("  all               - Run all tests")
        return
    
    test_name = sys.argv[1]
    
    if test_name == "all":
        tests = ["test_db_queries", "test_player_filter", "create_indexes"]
        print("🧪 Running all tests...")
        
        success_count = 0
        for test in tests:
            if run_test(test):
                success_count += 1
            print()
        
        print(f"✅ {success_count}/{len(tests)} tests passed")
        return
    
    success = run_test(test_name)
    if success:
        print(f"✅ {test_name} passed")
    else:
        print(f"❌ {test_name} failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 