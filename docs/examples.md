# Example Automations

Here are some example automations that you can build with Opsdroid.

## Sun based lights

The following skill turns a light on a sunset and off again at sunrise.

```python
from opsdroid_homeassistant import HassSkill, match_sunrise, match_sunset


class SunriseSkill(HassSkill):

    @match_sunset
    async def lights_on_at_sunset(self, event):
        await self.turn_on("light.outside")

    @match_sunrise
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
        if await self.sun_down():
            await self.turn_on("light.drive")
            for _ in range(10):
                await self.toggle("light.living_room_lamp")
                await sleep(1)
            await sleep(50)
            await self.turn_off("light.drive")
```

## Motion camera notification

The following skill takes a snapshot of a camera when motion is detected and pushes it to an Android device as a notification (in this example a notification target called `notify.mobile_app_pixel_4`).

```eval_rst
.. note::
    This skill assumes you have Home Assistant Cloud as notification images need to be accessible on the internet.
```

```python
from asyncio import sleep

from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class MotionCamera(HassSkill):

    @match_hass_state_changed("binary_sensor.drive", state="on")
    async def motion_camera(self, event):

        # Snapshot camera to a the local `www` folder
        await self.call_service(
            "camera",
            "snapshot",
            entity_id="camera.drive",
            filename="/config/www/cameras/camera.drive.jpg",
        )

        # Wait for the snapshot to save
        await sleep(1)

        # Send a notification with the image linked via Home Assistant Cloud
        await self.notify(
            "Camera Update",
            title="Motion detected",
            target="mobile_app_pixel_4",
            data={
                "android": {
                    "notification": {
                        "image": "https://<Your Home Assistant Cloud ID>.ui.nabu.casa/local/cameras/camera.drive.jpg"
                    }
                }
            },
        )
```

## Tortoise lights

I own a Mediterranean tortoise but live in a slightly colder climate and therefore he needs some artificial UV lighting on dull days. But if the natural sunlight is strong enough I don't want to waste power on the lighting.

This is an example of the skill I use to automate the lights.

```eval_rst
.. note::
    I use the Met Office sensor to get the UV information.
```

```python
from asyncio import sleep

from opsdroid_homeassistant import HassSkill, match_hass_state_changed, natch_sunrise, match_sunset


class MotionCamera(HassSkill):

    @match_sunrise
    @match_sunset
    @match_hass_state_changed("sensor.met_office_uv")
    async def tortoise_lamp(self, event):
        uv = int(await self.get_state("sensor.met_office_uv"))
        if await self.sun_up() and uv < 5:
            self.turn_on("switch.tortoise")
        else:
            self.turn_off("switch.tortoise")
```
