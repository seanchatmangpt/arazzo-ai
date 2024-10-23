"""Test arazzo-ai."""

import arazzo_ai


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(arazzo_ai.__name__, str)
