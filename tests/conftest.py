import pytest
import asyncio
from typing import Generator

# Configure pytest-asyncio to use function scope for pytest fixtures
@pytest.fixture(scope="function")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
