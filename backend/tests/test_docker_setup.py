# Simple test to verify Docker test setup
import pytest


def test_basic_functionality():
    """Basic test to verify pytest is working in Docker."""
    assert 1 + 1 == 2


def test_environment_variable():
    """Test that environment variables are accessible."""
    import os
    testing_env = os.getenv('TESTING', 'false')
    assert testing_env == 'true'


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality works in Docker."""
    async def sample_async_function():
        return "async_result"
    
    result = await sample_async_function()
    assert result == "async_result"