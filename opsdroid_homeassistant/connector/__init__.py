import json
import logging
import urllib.parse

import aiohttp
from voluptuous import Required

from opsdroid.connector import Connector, register_event
from opsdroid.events import Event

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = {
    Required("token"): str,
    Required("url"): str,
}


class HassEvent(Event):
    """Event class to represent a Home Assistant event."""


class HassServiceCall(Event):
    """Event class to represent making a service call in Home Assistant."""

    def __init__(self, domain, service, data, *args, **kwargs):
        self.domain = domain
        self.service = service
        self.data = data
        super().__init__(*args, **kwargs)


class HassConnector(Connector):
    """An opsdroid connector for syncing events with the Home Assistant event loop.

    """
    def __init__(self, config, opsdroid=None):
        super().__init__(config, opsdroid=opsdroid)
        self.name = "homeassistant"
        self.default_target = None
        self.connection = None
        self.url = urllib.parse.urljoin(self.config.get("url"), "/api/websocket")
        self.id = 1

    def _get_next_id(self):
        self.id = self.id + 1
        return self.id

    async def connect(self):
        pass

    async def listen(self):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.url) as ws:
                self.connection = ws
                async for msg in self.connection:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_message(json.loads(msg.data))
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

    async def _handle_message(self, msg):
        msg_type = msg.get("type")

        if msg_type == "auth_required":
            await self.connection.send_json(
                {"type": "auth", "access_token": self.config.get("token")}
            )

        if msg_type == "auth_invalid":
            _LOGGER.error("Invalid Home Assistant auth token.")
            await self.disconnect()

        if msg_type == "auth_ok":
            _LOGGER.info("Authenticated with Home Assistant.")
            await self.connection.send_json(
                {
                    "id": self._get_next_id(),
                    "type": "subscribe_events",
                    "event_type": "state_changed",
                }
            )

        if msg_type == "event":
            event = HassEvent(None, None, None, self, raw_event=msg)
            await event.update_entity("event_type", msg["event"]["event_type"])
            await event.update_entity("entity_id", msg["event"]["data"]["entity_id"])
            await event.update_entity(
                "state", msg["event"]["data"]["new_state"]["state"]
            )
            changed = (
                msg["event"]["data"]["new_state"]["state"]
                != msg["event"]["data"]["old_state"]["state"]
            )
            await event.update_entity("changed", changed)
            await self.opsdroid.parse(event)

        if msg_type == "result":
            if msg["success"]:
                pass
            else:
                _LOGGER.error("%s - %s", msg["error"]["code"], msg["error"]["message"])

    @register_event(HassServiceCall)
    async def send_service_call(self, event):
        await self.connection.send_json(
            {
                "id": self._get_next_id(),
                "type": "call_service",
                "domain": event.domain,
                "service": event.service,
                "service_data": event.data,
            }
        )

    async def disconnect(self):
        await self.connection.close()
