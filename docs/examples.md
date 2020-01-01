# Examples

Here are some example automations that you can build with Opsdroid.

## Sun based lights

The following skill turns a light on a sunset and off again at sunrise.

```python
from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class SunriseSkill(HassSkill):

    @match_hass_state_changed("sun.sun", state="below_horizon")
    async def lights_on_at_sunset(self, event):
        await self.turn_on("light.outside")

    @match_hass_state_changed("sun.sun", state="above_horizon")
    async def lights_off_at_sunrise(self, event):
        await self.turn_off("light.outside")
```

## Motion lights

The following Skill turns on an outside light for one minute when it detects motion and also flashes a lamp to notify people inside.

```python
from asyncio import sleep
from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class MotionLights(HassSkill):

    @match_hass_state_changed("binary_sensor.drive", state="on")
    async def motion_lights(self, event):
        await self.turn_on("light.drive")
        for _ in range(10):
            await self.toggle("light.living_room_lamp")
            await sleep(1)
        await sleep(50)
        await self.turn_off("light.drive")
```
