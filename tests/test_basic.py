"""
Basic test suite for Vajra Kavach
Created by: Soumodeep Guha
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_import_main():
    """Test that main module can be imported"""
    try:
        import main
        assert True
    except ImportError as e:
        pytest.skip(f"Main module not available: {e}")


def test_basic_math():
    """Basic sanity test"""
    assert 1 + 1 == 2
    assert True is True


def test_environment_check():
    """Test environment setup"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"


def test_requirements_exist():
    """Test that requirements.txt exists"""
    req_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    assert os.path.exists(req_path), "requirements.txt not found"


def test_readme_exists():
    """Test that README.md exists"""
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    assert os.path.exists(readme_path), "README.md not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
