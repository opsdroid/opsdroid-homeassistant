# Getting Started

## Installation

```console
pip install opsdroid-homeassistant
```

## Example Skill

To create our first skill we need to create a Python file. You can either create a standalone file
or a module that can be imported.

Let's create a new file called `/home/user/opsdroid-skills/myskill.py`. This can be anywhere you like
but keep note of the path as we will need it in our config later.

```python
from asyncio import sleep
from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class MotionLights(HassSkill):

    @match_hass_state_changed("binary_sensor.drive", state="on")
    async def motion_lights(self, event):
        """Turn the outside light on with motion if after sunset."""
        if await self.sun_down():
            await self.turn_on("light.drive")
            await sleep(60)
            await self.turn_off("light.drive")
```

## Example configuration

Next we need to edit our Opsdroid configuration to tell it about Home Assistant
and our new skill.

You can open your config in an editor by running

```console
$ opsdroid config edit
```

```eval_rst
.. note::
    You can set the ``EDITOR`` environment variable to your preferred editor and opsdroid
    will automatically open your config in that.
```

```yaml
## Set the logging level
logging:
  level: info

## Show welcome message
welcome-message: true

## Connector modules
connectors:
  homeassistant:
    url: http://localhost:8123/
    token: mytoken

## Skill modules
skills:
  example:
    path: /home/user/opsdroid-skills/myskill.py
```

In the above configuration we are enabling the Home Assistant connector. We need to give it the URL
of our Home Assistant and a [Long Lived Access Token](https://www.home-assistant.io/docs/authentication/).

We also configure our skill with the path to the Python file we created.

## Running Opsdroid

Now we can start Opsdroid with:

```console
$ opsdroid start
```

For more information on installing and configuring Opsdroid [see the documentation](https://docs.opsdroid.dev/en/stable/index.html).
