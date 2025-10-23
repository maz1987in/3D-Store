"""
Pytest configuration for app-level tests.

This file enables pytest to discover fixtures from the main test/conftest.py
when running tests from app/*/test.py locations.
"""

import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add test directory to Python path
test_dir = os.path.join(parent_dir, 'test')
if test_dir not in sys.path:
    sys.path.insert(0, test_dir)

# Import all fixtures from main conftest
from test.conftest import *

