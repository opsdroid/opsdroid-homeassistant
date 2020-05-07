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
    assert not (await mock_skill.sun_up() and await mock_skill.sun_down())

    if await mock_skill.sun_up():
        assert await mock_skill.sunset() < await mock_skill.sunrise()
    else:
        assert await mock_skill.sunset() > await mock_skill.sunrise()


@pytest.mark.asyncio
async def test_presence(mock_skill):
    assert isinstance(await mock_skill.anyone_home(), bool)
    assert isinstance(await mock_skill.everyone_home(), bool)
    assert isinstance(await mock_skill.nobody_home(), bool)
    assert isinstance(await mock_skill.get_trackers(), list)


@pytest.mark.asyncio
async def test_template_render(mock_skill):
    template = await mock_skill.render_template(
        "Paulus is {{ states('device_tracker.demo_paulus') }}!"
    )
    assert template == "Paulus is not_home!"


@pytest.mark.asyncio
async def test_notify(mock_skill):
    await mock_skill.notify("Hello world")
    # TODO Assert something to check the notification fired correctly


@pytest.mark.asyncio
async def test_update_entity(connector, mock_skill):
    entity = "sensor.outside_temperature"
    original_temp = await mock_skill.get_state(entity)

    await connector.query_api("states/" + entity, method="POST", state=0)
    assert await mock_skill.get_state(entity) == "0"

    await mock_skill.update_entity(entity)
    assert original_temp == await mock_skill.get_state(entity)


@pytest.mark.asyncio
async def test_set_value(mock_skill, caplog):
    assert await mock_skill.get_state("input_number.slider1") == "30.0"
    await mock_skill.set_value("input_number.slider1", 20)
    assert await mock_skill.get_state("input_number.slider1") == "20.0"

    assert await mock_skill.get_state("input_text.text1") == "Some Text"
    await mock_skill.set_value("input_text.text1", "Hello world")
    assert await mock_skill.get_state("input_text.text1") == "Hello world"

    assert await mock_skill.get_state("input_select.who_cooks") == "Anne Therese"
    await mock_skill.set_value("input_select.who_cooks", "Paulus")
    assert await mock_skill.get_state("input_select.who_cooks") == "Paulus"

    await mock_skill.set_value("light.bed_light", "Foo")
    assert "unsupported entity light.bed_light" in caplog.text
