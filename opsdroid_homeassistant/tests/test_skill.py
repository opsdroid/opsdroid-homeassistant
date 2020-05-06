import pytest

from asyncio import sleep

from opsdroid.events import Message


@pytest.mark.asyncio
async def test_turn_on_off_toggle(opsdroid, mock_skill):
    assert await mock_skill.get_state("light.bed_light") == "off"

    await opsdroid.parse(Message("Turn on the light"))
    await sleep(0.1)
    assert await mock_skill.get_state("light.bed_light") == "on"

    await opsdroid.parse(Message("Turn off the light"))
    await sleep(0.1)
    assert await mock_skill.get_state("light.bed_light") == "off"

    await opsdroid.parse(Message("Toggle the light"))
    await sleep(0.1)
    assert await mock_skill.get_state("light.bed_light") == "on"

    await opsdroid.parse(Message("Toggle the light"))
    await sleep(0.1)
    assert await mock_skill.get_state("light.bed_light") == "off"


@pytest.mark.asyncio
async def test_sun_states(mock_skill):
    from datetime import datetime

    assert isinstance(await mock_skill.sun_up(), bool)
    assert isinstance(await mock_skill.sun_down(), bool)
    assert isinstance(await mock_skill.sunset(), datetime)
    assert isinstance(await mock_skill.sunrise(), datetime)

    assert await mock_skill.sun_up() or await mock_skill.sun_down()
    assert not await mock_skill.sun_up() and await mock_skill.sun_down()

    if await mock_skill.sun_up():
        assert await mock_skill.sunset() < await mock_skill.sunrise()
    else:
        assert await mock_skill.sunset() > await mock_skill.sunrise()
