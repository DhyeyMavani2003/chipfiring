#!/usr/bin/env python3

"""
Script to run the test suite.
"""

import pytest
import sys


def main():
    """Run the test suite."""
    # Add the current directory to the Python path
    sys.path.insert(0, ".")
    
    # Run pytest with verbosity and show warnings
    sys.exit(pytest.main(["-v", "-W", "ignore::DeprecationWarning"]))


if __name__ == "__main__":
    main() 