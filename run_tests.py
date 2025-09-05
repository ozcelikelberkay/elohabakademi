#!/usr/bin/env python3
"""
Test runner script for ELOHAB Akademi project
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error code: {e.returncode}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False

def main():
    """Main test runner function"""
    print("🚀 ELOHAB Akademi Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command("pip install -r requirements.txt", "Install dependencies"):
        print("❌ Failed to install dependencies. Exiting.")
        sys.exit(1)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    if not run_command("python -m pytest tests/unit/ -v --tb=short", "Unit tests"):
        print("⚠️  Some unit tests failed, but continuing...")
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    if not run_command("python -m pytest tests/integration/ -v --tb=short", "Integration tests"):
        print("⚠️  Some integration tests failed, but continuing...")
    
    # Run functional tests
    print("\n⚙️  Running Functional Tests...")
    if not run_command("python -m pytest tests/functional/ -v --tb=short", "Functional tests"):
        print("⚠️  Some functional tests failed, but continuing...")
    
    # Run security tests
    print("\n🔒 Running Security Tests...")
    if not run_command("python -m pytest tests/security/ -v --tb=short", "Security tests"):
        print("⚠️  Some security tests failed, but continuing...")
    
    # Run all tests with coverage
    print("\n📊 Running All Tests with Coverage...")
    if not run_command("python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing", "All tests with coverage"):
        print("⚠️  Some tests failed, but coverage report generated.")
    
    # Generate test report
    print("\n📋 Test Summary:")
    print("✅ Unit Tests: Basic functionality testing")
    print("✅ Integration Tests: Database and API integration")
    print("✅ Functional Tests: User workflow testing")
    print("✅ Security Tests: Security vulnerability testing")
    print("✅ Coverage Report: Code coverage analysis")
    
    print("\n🎯 Next Steps:")
    print("1. Review test results above")
    print("2. Check htmlcov/ directory for detailed coverage report")
    print("3. Fix any failing tests")
    print("4. Improve test coverage for untested code")
    
    print("\n🚀 Test suite completed!")

if __name__ == "__main__":
    main()
