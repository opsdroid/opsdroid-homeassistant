import pytest

from opsdroid_homeassistant import HassConnector


@pytest.fixture
def dummy_config():
    return {"token": "abc123", "url": "https://example.com:8123"}


def test_attributes(dummy_config):
    connector = HassConnector(dummy_config, opsdroid=None)

    assert connector.name == "homeassistant"
    assert connector.default_target is None
