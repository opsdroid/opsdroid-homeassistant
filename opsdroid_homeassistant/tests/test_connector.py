import pytest
import requests

from opsdroid_homeassistant import HassConnector


@pytest.fixture
def dummy_config():
    return {"token": "abc123", "url": "http://127.0.0.1:8123"}


def test_attributes(dummy_config):
    connector = HassConnector(dummy_config, opsdroid=None)

    assert connector.name == "homeassistant"
    assert connector.default_target is None


def test_hass(homeassistant, access_token):
    response = requests.get(
        homeassistant, headers={"Authorization": "Bearer " + access_token}
    )
    assert response.status_code == 200
