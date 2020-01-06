import arrow
from datetime import datetime
import logging

from opsdroid.skill import Skill

from ..connector import HassServiceCall

_LOGGER = logging.getLogger(__name__)


class HassSkill(Skill):
    """An Opsdroid skill base class with Home Assistant helper methods.

    To create a Home Assistant skill for your Opsdroid bot you need to subclass
    this class and define methods which are decorated with matchers. For triggering skills on
    Home Assistant events you will likely want to use the
    :func:`opsdroid_homeassistant.match_hass_state_changed` matcher.

    This base class also has some helper functions such as :meth:`turn_on` and :meth:`turn_off`
    to make it quick and convenient to control your Home Assistant entities. See the methods
    below for more information.

    Examples:

       Turning a light on at sunset::

            from opsdroid_homeassistant import HassSkill, match_hass_state_changed


            class SunriseSkill(HassSkill):

                @match_hass_state_changed("sun.sun", state="below_horizon")
                async def lights_on_at_sunset(self, event):
                    await self.turn_on("light.outside")

    For detailed information on writing skills check out the Opsdroid skill docs
    https://docs.opsdroid.dev/en/stable/skills/index.html.

    """

    def __init__(self, opsdroid, config, *args, **kwargs):
        super().__init__(opsdroid, config, *args, **kwargs)
        [self.hass] = [
            connector
            for connector in self.opsdroid.connectors
            if connector.name == "homeassistant"
        ]

    async def call_service(self, domain: str, service: str, *args, **kwargs):
        """Send a service call to Home Assistant.

        Build your own service call to any domain and service.

        Note:
            For common operations such and turning off and on entities see
            the :meth:`turn_on` and :meth:`turn_off` helper functions.
        """
        await self.hass.send(HassServiceCall(domain, service, kwargs))

    async def get_state(self, entity: str):
        """Get the state of an entity.

        Args:
            entity: The ID of the entity to get the state for.

        Returns:
            The state of the entity.

        Examples:
            Get the state of the sun sensor::

                >>> await self.get_state("sun.sun")
                "above_horizon"
        """
        state = await self.hass.query_api("states/" + entity)
        _LOGGER.debug(state)
        return state.get("state", None)

    async def turn_on(self, entity_id: str, **kwargs):
        """Turn on an entity in Home Assistant.

        Sends a ``homeassistant.turn_on`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "turn_on", entity_id=entity_id, **kwargs
        )

    async def turn_off(self, entity_id: str, **kwargs):
        """Turn off an entity in Home Assistant.

        Sends a ``homeassistant.turn_off`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "turn_off", entity_id=entity_id, **kwargs
        )

    async def toggle(self, entity_id: str, **kwargs):
        """Toggle an entity in Home Assistant.

        Sends a ``homeassistant.toggle`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "toggle", entity_id=entity_id, **kwargs
        )

    async def update_entity(self, entity_id: str, **kwargs):
        """Request an entity update in Home Assistant.

        Sends a ``homeassistant.update_entity`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "update_entity", entity_id=entity_id, **kwargs
        )

    async def set_value(self, entity_id: str, value, **kwargs):
        """Sets an entity to the specified value in Home Assistant.

        Depending on the entity type provided one of the following services will be called:

        * ``input_number.set_value``
        * ``input_text.set_value``
        * ``input_select.select_option``

        """
        if "input_number" in entity_id:
            await self.call_service(
                "input_number", "set_value", entity_id=entity_id, value=value, **kwargs
            )
        elif "input_text" in entity_id:
            await self.call_service(
                "input_text", "set_value", entity_id=entity_id, value=value, **kwargs
            )
        elif "input_select" in entity_id:
            await self.call_service(
                "input_select",
                "select_option",
                entity_id=entity_id,
                option=value,
                **kwargs
            )
        else:
            _LOGGER.error("Unable to set value for unsupported entity %s", entity_id)

    async def notify(
        self, message: str, title="Home Assistant", target="notify", **kwargs
    ):
        """Send a notification to Home Assistant.

        Sends a ``notify.notify`` service call with the specified title and message.

        Args:
            message: A message to notify with.
            title (optional): A title to set in the notification.
            target (optional): The notification target. Defaults to ``notify`` which will notify all.
        """
        await self.call_service(
            "notify", target, message=message, title=title, **kwargs
        )

    async def sun_up(self):
        """Check whether the sun is up.

        Returns:
            True if sun is up, else False.

        """
        sun_state = await self.get_state("sun.sun")
        return sun_state == "above_horizon"

    async def sun_down(self):
        """Check whether the sun is down.

        Returns:
            True if sun is down, else False.

        """
        sun_state = await self.get_state("sun.sun")
        return sun_state == "below_horizon"

    async def sunrise(self):
        """Get the timestamp for the next sunrise.

        Returns:
            A Datetime object of next sunrise.

        """
        sun_state = await self.hass.query_api("states/sun.sun")
        sunrise = arrow.get(sun_state["attributes"]["next_rising"])
        return sunrise.datetime

    async def sunset(self):
        """Get the timestamp for the next sunset.

        Returns:
            A Datetime object of next sunset.

        """
        sun_state = await self.hass.query_api("states/sun.sun")
        sunset = arrow.get(sun_state["attributes"]["next_setting"])
        return sunset.datetime

    async def get_trackers(self):
        """Get a list of tracker entities from Home Assistant.

        Returns:
            List of tracker dictionary objects.

        Examples:

            >>> await self.get_trackers()
            [{
                "attributes": {
                    "entity_picture": "https://www.gravatar.com/avatar/00000000000000000000000000000000?s=500&d=mm",
                    "friendly_name": "jacob",
                    "ip": "192.168.0.2",
                    "scanner": "NmapDeviceScanner",
                    "source_type": "router"
                },
                "context": {
                    "id": "abc123",
                    "parent_id": None,
                    "user_id": None
                },
                "entity_id": "device_tracker.jacob",
                "last_changed": "2020-01-03T20:27:55.001812+00:00",
                "last_updated": "2020-01-03T20:27:55.001812+00:00",
                "state": "home"
            }]

        """
        states = await self.hass.query_api("states")
        device_trackers = [
            entity
            for entity in states
            if entity["entity_id"].startswith("device_tracker.")
        ]
        return device_trackers

    async def anyone_home(self):
        """Check if anyone is home.

        Returns:
            True if any tracker is set to ``home``, else False.

        """
        trackers = await self.get_trackers()
        home = [tracker["state"] == "home" for tracker in trackers]
        return any(home)

    async def everyone_home(self):
        """Check if everyone is home.

        Returns:
            True if all trackers are set to ``home``, else False.

        """
        trackers = await self.get_trackers()
        home = [tracker["state"] == "home" for tracker in trackers]
        return all(home)

    async def nobody_home(self):
        """Check if nobody is home.

        Returns:
            True if all trackers are set to ``not_home``, else False.

        """
        trackers = await self.get_trackers()
        not_home = [tracker["state"] == "not_home" for tracker in trackers]
        return all(not_home)

    async def render_template(self, template: str) -> str:
        """Ask Home Assistant to render a template.

        Home Assistant has a built in templating engine powered by Jinja2.

        https://www.home-assistant.io/docs/configuration/templating/

        This method allows you to pass a template string to Home Assistant and
        it will return the formatted response.

        Args:
            template: The template string to be rendered by Home Assistant.

        Returns:
            A formatted string of the template.

        Examples:

            >>> await self.render_template("Jacob is at {{ states('device_tracker.jacob') }}!")
            Jacob is at home!

        """
        return await self.hass.query_api(
            "template", method="POST", decode_json=False, template=template
        )
