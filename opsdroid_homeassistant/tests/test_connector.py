import pytest
import requests

from opsdroid_homeassistant import HassConnector


@pytest.fixture
def config(homeassistant, access_token):
    return {"token": access_token, "url": homeassistant}


@pytest.fixture
def connector(config):
    return HassConnector(config, opsdroid=None)


def test_attributes(connector):
    assert connector.name == "homeassistant"
    assert connector.default_target is None


@pytest.mark.asyncio
async def test_connect(connector):
    await connector.connect()
    assert connector.listening
    assert "version" in connector.discovery_info
