import pytest
from asyncio import sleep


@pytest.mark.asyncio
async def test_match_hass_state_changed(mock_skill):
    test_entity = "light.kitchen_lights"

    assert await mock_skill.get_state(test_entity) == "on"
    assert not mock_skill.kitchen_lights_changed

    await mock_skill.toggle(test_entity)
    await sleep(0.1)  # Give Home Assistant a chance to update

    assert await mock_skill.get_state(test_entity) == "off"
    assert mock_skill.kitchen_lights_changed
