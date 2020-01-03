from typing import Callable

from opsdroid.matchers import match_event
from ..connector import HassEvent


def match_hass_state_changed(entity_id: str, **kwargs) -> Callable:
    """A matcher for state changes in Home Assistant.

    When an entity changes state in Home Assistant an event is triggered in Opsdroid.
    This matcher can be used to watch for a specific entity to change state::

        from opsdroid_homeassistant import HassSkill, match_hass_state_changed


        class SunriseSkill(HassSkill):

            @match_hass_state_changed("sun.sun", state="below_horizon")
            async def lights_on_at_sunset(self, event):
                await self.turn_on("light.outside")

    Alternatively you can use the :func:`opsdroid.matchers.match_event` matcher from the core Opsdroid set
    of matchers along with the :class:`opsdroid_homeassistant.HassEvent` class from opsdroid-homeassistant.
    With this method you much specify the entity with the kwarg ``entity_id`` and set ``changed=True`` if you
    only wish for the skill to trigger when the state changes. Sometimes entities send an event even if the
    state hasn't changed::

        from opsdroid.matchers import match_event
        from opsdroid_homeassistant import HassSkill, HassEvent


        class SunriseSkill(HassSkill):

            @match_event(HassEvent, entity_id="sun.sun", changed=True, state="below_horizon")
            async def lights_on_at_sunset(self, event):
                await self.turn_on("light.outside")

    Args:
        entity_id: The full domain and name of the entity you want to watch. e,g ``sun.sun``
        state (optional): The state you want to watch for. e.g ``on``

    """
    return match_event(HassEvent, entity_id=entity_id, changed=True, **kwargs)
