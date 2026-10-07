import pathlib
import sys

import pytest

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _postgres_url() -> str | None:
    import os

    for name in ("SPIKE_DATABASE_URL", "DATABASE_URL"):
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return None


@pytest.fixture(scope="session")
def postgres_url() -> str:
    url = _postgres_url()
    if not url:
        pytest.skip("No SPIKE_DATABASE_URL/DATABASE_URL set; skipping Postgres integration test")
    return url
