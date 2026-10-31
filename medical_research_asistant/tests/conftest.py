import sys
from pathlib import Path

import pytest

# Ensure src directory is in sys.path for test discovery
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

