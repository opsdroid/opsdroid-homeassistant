from opsdroid.matchers import match_regex
from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class TestSkill(HassSkill):
    def __init__(self, opsdroid, config, *args, **kwargs):
        super().__init__(opsdroid, config, *args, **kwargs)
        opsdroid.mock_skill = self
        self.kitchen_lights_changed = False

    @match_regex(r"Turn on the light")
    async def lights_on(self, event):
        await self.turn_on("light.bed_light")

    @match_regex(r"Turn off the light")
    async def lights_off(self, event):
        await self.turn_off("light.bed_light")

    @match_regex(r"Toggle the light")
    async def lights_toggle(self, event):
        await self.toggle("light.bed_light")

    @match_hass_state_changed("light.kitchen_lights")
    async def listen_for_lights(self, event):
        self.kitchen_lights_changed = True
