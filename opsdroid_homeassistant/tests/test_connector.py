import pytest

from asyncio import sleep

from opsdroid.events import Message


@pytest.mark.asyncio
async def test_attributes(connector):
    assert connector.name == "homeassistant"
    assert connector.default_target is None


@pytest.mark.asyncio
async def test_connect(connector):
    assert connector.listening
    assert "version" in connector.discovery_info
