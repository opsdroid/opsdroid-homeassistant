# Alternatives

Here are some objective comparisons between the Opsdroid Home Assistant bridge and other similar projects.

## AppDaemon

[AppDaemon](https://appdaemon.readthedocs.io/en/latest/) is a well established Python framework for creating Home Assistant automations.

You write your automations as generic Python classes and then configure them using YAML files. Your Python code needs to use a callback model where you define methods in your class which perform the actions you want to happen and then in an `initialize` method you register your callbacks with methods like `run_at`, `run_daily` or `listen_state`.

Opsdroid uses [asyncio](https://docs.python.org/3/library/asyncio.html) to handle concurrency. Automations are also defined as methods on a class but you use decorators like `match_hass_state_changed`, `match_crontab`, `match_webhook`, etc to define when your functions should be called.

The differences in the way they handle concurrency is most noticeable when setting up timelines. In AppDaemon you must register a series of callbacks at the specified times which can result in a complex chain of callbacks.

```python
import appdaemon.plugins.hass.hassapi as hass

class MotionLights(hass.Hass):

    def initialize(self):
        self.listen_state(self.motion, "binary_sensor.drive", new="on")

    def motion(self, entity, attribute, old, new, kwargs):
        self.turn_on("light.drive")
        self.run_in(self.light_off, 60)
        self.flashcount = 0
        self.run_in(self.flash_warning, 1)

    def light_off(self, kwargs):
        self.turn_off("light.drive")

    def flash_warning(self, kwargs):
        self.toggle("light.living_room")
        self.flashcount += 1
        if self.flashcount < 10:
            self.run_in(self.flash_warning, 1)
```

In the above example we are registering our `motion` method to be called when a motion sensor changes state to `on`. We then turn on a light and register a callback to turn it off again in 60 seconds. Then in the mean time we register a recursive callback which toggles another light 10 times over 10 seconds.

In opsdroid we would define something like this.

```python
from asyncio import sleep
from opsdroid_homeassistant import HassSkill, match_hass_state_changed


class MotionLights(HassSkill):

    @match_hass_state_changed("binary_sensor.drive", state="on")
    async def motion_lights(self, event):
        await self.turn_on("light.drive")
        for _ in range(10):
            await self.toggle("light.living_room")
            await sleep(1)
        await sleep(50)  # Because 10 seconds have already elapsed
        await self.turn_off("light.drive")
```

Here we can see we just have one method which contains all of our logic. The flow is laid out in order of what we want to happen, we perform an action, then sleep the amount of time we want to wait, then perform the next action. This makes our automation much more readable. As we are using asyncio we are able to run this concurrently with other skills thanks to the `async`/`await` syntax. A downside to this approach is that each sleep needs to be a time delta, if we want our drive light to turn off after 60 seconds we need to keep track of how long we've slept since turning it on.

### Reasons to choose AppDaemon

* Stability and maturity, AppDaemon is at version 3
* Tight integration, AppDaemon has many more Home Assistant helper functions
* Community, AppDaemon is a Home Assistant community project
* Doesn't use asyncio, which has a small learning curve
* You want to use the built in [HADashboard dashboards](https://appdaemon.readthedocs.io/en/latest/DASHBOARD_INSTALL.html)

### Reasons to choose Opsdroid

* More readable automation code
* You're building a chatbot and want to use the [AI and NLP capabilities](https://docs.opsdroid.dev/en/stable/skills/index.html#matchers) of Opsdroid
* You want to natively trigger automations on external events like cron timings or webhooks
