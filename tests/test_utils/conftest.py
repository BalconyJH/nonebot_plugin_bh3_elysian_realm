from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest


@pytest.fixture
def temp_json_file():
    with NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        temp_path = Path(tmp.name)
    yield temp_path
    temp_path.unlink()
