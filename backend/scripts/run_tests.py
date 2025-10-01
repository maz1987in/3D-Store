#!/usr/bin/env python3
"""
Test runner script for the 3D Store backend.

This script provides a convenient way to run different types of tests
with various configurations and options.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, cwd=backend_dir, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    cmd = ['python', '-m', 'pytest', 'test/test_unit/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, "Unit Tests")

def run_integration_tests(verbose=False, coverage=False):
    """Run integration tests."""
    cmd = ['python', '-m', 'pytest', 'test/test_integration/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, "Integration Tests")

def run_api_tests(verbose=False, coverage=False):
    """Run API tests."""
    cmd = ['python', '-m', 'pytest', 'test/test_api/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, "API Tests")

def run_database_tests(verbose=False, coverage=False):
    """Run database tests."""
    cmd = ['python', '-m', 'pytest', 'test/test_database/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, "Database Tests")

def run_all_tests(verbose=False, coverage=False):
    """Run all tests."""
    cmd = ['python', '-m', 'pytest', 'test/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, "All Tests")

def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function."""
    cmd = ['python', '-m', 'pytest', test_path]
    
    if verbose:
        cmd.append('-v')
    
    return run_command(cmd, f"Specific Test: {test_path}")

def run_tests_by_marker(marker, verbose=False, coverage=False):
    """Run tests by marker."""
    cmd = ['python', '-m', 'pytest', f'-m', marker]
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=app', '--cov-report=html', '--cov-report=term'])
    
    return run_command(cmd, f"Tests with marker: {marker}")

def run_slow_tests(verbose=False):
    """Run slow tests."""
    return run_tests_by_marker('slow', verbose)

def run_fast_tests(verbose=False):
    """Run fast tests (exclude slow tests)."""
    cmd = ['python', '-m', 'pytest', '-m', 'not slow']
    
    if verbose:
        cmd.append('-v')
    
    return run_command(cmd, "Fast Tests (excluding slow tests)")

def run_tests_with_coverage():
    """Run all tests with coverage report."""
    cmd = [
        'python', '-m', 'pytest', 
        'test/',
        '--cov=app',
        '--cov-report=html',
        '--cov-report=term',
        '--cov-report=xml',
        '--cov-fail-under=80'
    ]
    
    return run_command(cmd, "All Tests with Coverage")

def run_tests_parallel(workers=4):
    """Run tests in parallel."""
    cmd = [
        'python', '-m', 'pytest',
        'test/',
        '-n', str(workers),
        '--dist=loadfile'
    ]
    
    return run_command(cmd, f"Parallel Tests ({workers} workers)")

def run_tests_with_profiling():
    """Run tests with profiling."""
    cmd = [
        'python', '-m', 'pytest',
        'test/',
        '--profile',
        '--profile-svg'
    ]
    
    return run_command(cmd, "Tests with Profiling")

def run_tests_verbose():
    """Run tests with maximum verbosity."""
    cmd = [
        'python', '-m', 'pytest',
        'test/',
        '-vv',
        '--tb=long',
        '--capture=no'
    ]
    
    return run_command(cmd, "Verbose Tests")

def run_tests_debug():
    """Run tests in debug mode."""
    cmd = [
        'python', '-m', 'pytest',
        'test/',
        '--pdb',
        '--pdb-trace',
        '-s'
    ]
    
    return run_command(cmd, "Debug Tests")

def run_tests_ci():
    """Run tests in CI mode."""
    cmd = [
        'python', '-m', 'pytest',
        'test/',
        '--cov=app',
        '--cov-report=xml',
        '--cov-report=term',
        '--junitxml=test-results.xml',
        '--tb=short'
    ]
    
    return run_command(cmd, "CI Tests")

def lint_code():
    """Run code linting."""
    cmd = ['python', '-m', 'flake8', 'app/', 'test/']
    return run_command(cmd, "Code Linting")

def format_code():
    """Format code."""
    cmd = ['python', '-m', 'black', 'app/', 'test/']
    return run_command(cmd, "Code Formatting")

def type_check():
    """Run type checking."""
    cmd = ['python', '-m', 'mypy', 'app/']
    return run_command(cmd, "Type Checking")

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Run tests for the 3D Store backend')
    
    # Test type arguments
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--api', action='store_true', help='Run API tests')
    parser.add_argument('--database', action='store_true', help='Run database tests')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    # Test execution arguments
    parser.add_argument('--test', type=str, help='Run specific test file or function')
    parser.add_argument('--marker', type=str, help='Run tests with specific marker')
    parser.add_argument('--slow', action='store_true', help='Run slow tests')
    parser.add_argument('--fast', action='store_true', help='Run fast tests (exclude slow)')
    
    # Test configuration arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage')
    parser.add_argument('--parallel', type=int, help='Run tests in parallel with N workers')
    parser.add_argument('--profile', action='store_true', help='Run with profiling')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--ci', action='store_true', help='Run in CI mode')
    
    # Code quality arguments
    parser.add_argument('--lint', action='store_true', help='Run code linting')
    parser.add_argument('--format', action='store_true', help='Format code')
    parser.add_argument('--type-check', action='store_true', help='Run type checking')
    
    # Combined arguments
    parser.add_argument('--quality', action='store_true', help='Run all code quality checks')
    parser.add_argument('--full', action='store_true', help='Run all tests with coverage and quality checks')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    success = True
    
    # Run code quality checks
    if args.lint or args.quality or args.full:
        success &= lint_code()
    
    if args.format or args.quality or args.full:
        success &= format_code()
    
    if args.type_check or args.quality or args.full:
        success &= type_check()
    
    # Run tests
    if args.unit:
        success &= run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success &= run_integration_tests(args.verbose, args.coverage)
    elif args.api:
        success &= run_api_tests(args.verbose, args.coverage)
    elif args.database:
        success &= run_database_tests(args.verbose, args.coverage)
    elif args.test:
        success &= run_specific_test(args.test, args.verbose)
    elif args.marker:
        success &= run_tests_by_marker(args.marker, args.verbose, args.coverage)
    elif args.slow:
        success &= run_slow_tests(args.verbose)
    elif args.fast:
        success &= run_fast_tests(args.verbose)
    elif args.parallel:
        success &= run_tests_parallel(args.parallel)
    elif args.profile:
        success &= run_tests_with_profiling()
    elif args.debug:
        success &= run_tests_debug()
    elif args.ci:
        success &= run_tests_ci()
    elif args.coverage:
        success &= run_tests_with_coverage()
    elif args.verbose:
        success &= run_tests_verbose()
    elif args.all or args.full:
        success &= run_all_tests(args.verbose, args.coverage)
    else:
        # Default: run all tests
        success &= run_all_tests(args.verbose, args.coverage)
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All tests passed successfully!")
        print(f"{'='*60}")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed!")
        print(f"{'='*60}")
        sys.exit(1)

if __name__ == '__main__':
    main()
