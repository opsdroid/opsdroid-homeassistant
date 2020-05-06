import pytest

from opsdroid.events import Message


@pytest.mark.asyncio
async def test_attributes(connector):
    assert connector.name == "homeassistant"
    assert connector.default_target is None


@pytest.mark.asyncio
async def test_connect(connector):
    assert connector.listening
    assert "version" in connector.discovery_info


@pytest.mark.asyncio
async def test_turn_on_off_toggle(opsdroid, test_skill):
    assert await test_skill.get_state("light.bed_light") == "off"

    await opsdroid.parse(Message("Turn on the light"))
    assert await test_skill.get_state("light.bed_light") == "on"

    await opsdroid.parse(Message("Turn off the light"))
    assert await test_skill.get_state("light.bed_light") == "off"

    await opsdroid.parse(Message("Toggle the light"))
    assert await test_skill.get_state("light.bed_light") == "on"

    await opsdroid.parse(Message("Toggle the light"))
    assert await test_skill.get_state("light.bed_light") == "off"
