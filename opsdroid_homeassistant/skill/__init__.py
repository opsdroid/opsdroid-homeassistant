import logging

from opsdroid.skill import Skill

from opsdroid_homeassistant.connector import HassServiceCall

_LOGGER = logging.getLogger(__name__)


class HassSkill(Skill):
    def __init__(self, opsdroid, config, *args, **kwargs):
        super().__init__(opsdroid, config, *args, **kwargs)
        [self.hass] = [
            connector
            for connector in self.opsdroid.connectors
            if connector.name == "homeassistant"
        ]

    async def call_service(self, domain, service, *args, **kwargs):
        await self.hass.send(HassServiceCall(domain, service, kwargs))

    async def turn_on(self, entity_id, **kwargs):
        await self.call_service(
            "homeassistant", "turn_on", entity_id=entity_id, **kwargs
        )

    async def turn_off(self, entity_id, **kwargs):
        await self.call_service(
            "homeassistant", "turn_off", entity_id=entity_id, **kwargs
        )

    async def toggle(self, entity_id, **kwargs):
        await self.call_service(
            "homeassistant", "toggle", entity_id=entity_id, **kwargs
        )

    async def update_entity(self, entity_id, **kwargs):
        await self.call_service(
            "homeassistant", "update_entity", entity_id=entity_id, **kwargs
        )

    async def set_value(self, entity_id, value, **kwargs):
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

    async def notify(self, title, message, **kwargs):
        await self.call_service(
            "notify", "notify", message=message, title=title, **kwargs
        )
