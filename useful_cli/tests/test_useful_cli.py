"""
Unit and regression test for the useful_cli package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import useful_cli


def test_useful_cli_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "useful_cli" in sys.modules
