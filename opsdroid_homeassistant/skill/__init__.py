import logging

from opsdroid.skill import Skill

from ..connector import HassServiceCall

_LOGGER = logging.getLogger(__name__)


class HassSkill(Skill):
    """An opsdroid skill base class with Home Assistant helper methods.

    To create a Home Assistant skill for your opsdroid bot you need to subclass
    this class and define methods which are decorated with matchers.

    This base class also has some helper functions such as :meth:`turn_on` and :meth:`turn_off`
    to make it quick and convenient to control your Home Assistant entities.

    For more information on writing skills check out the opsdroid skill docs
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
        """Send a service call to home assistant.

        Build your own service call to any domain and service.

        For common operations such and turning off and on entities see
        the :meth:`turn_on` and :meth:`turn_off` helper functions.
        """
        await self.hass.send(HassServiceCall(domain, service, kwargs))

    async def turn_on(self, entity_id: str, **kwargs):
        """Turn on an entity in home assistant.

        Sends a ``homeassistant.turn_on`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "turn_on", entity_id=entity_id, **kwargs
        )

    async def turn_off(self, entity_id: str, **kwargs):
        """Turn off an entity in home assistant.

        Sends a ``homeassistant.turn_off`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "turn_off", entity_id=entity_id, **kwargs
        )

    async def toggle(self, entity_id: str, **kwargs):
        """Toggle an entity in home assistant.

        Sends a ``homeassistant.toggle`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "toggle", entity_id=entity_id, **kwargs
        )

    async def update_entity(self, entity_id: str, **kwargs):
        """Request an entity update in home assistant.

        Sends a ``homeassistant.update_entity`` service call with the specified entity.
        """
        await self.call_service(
            "homeassistant", "update_entity", entity_id=entity_id, **kwargs
        )

    async def set_value(self, entity_id: str, value, **kwargs):
        """Sets an entity to the specified value in home assistant.

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

    async def notify(self, title: str, message: str, **kwargs):
        """Send a notification to home assistant.

        Sends a ``notify.notify`` service call with the specified title and message.
        """
        await self.call_service(
            "notify", "notify", message=message, title=title, **kwargs
        )
