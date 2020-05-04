import asyncio
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
        self.listening = None
        self.discovery_info = None
        self.token = self.config.get("token")
        self.api_url = urllib.parse.urljoin(self.config.get("url"), "api/")

        # The websocket URL can differ depending on how Home Assistant was installed.
        # So we will iterate over the various urls when attempting to connect.
        self.websocket_urls = [
            urllib.parse.urljoin(self.api_url, "websocket"),  # Plain Home Assistant
            urllib.parse.urljoin(self.config.get("url"), "websocket"),  # Hassio proxy
        ]
        self.id = 1

    def _get_next_id(self):
        self.id = self.id + 1
        return self.id

    async def connect(self):
        self.discovery_info = await self.query_api("discovery_info")
        self.listening = True

    async def listen(self):
        async with aiohttp.ClientSession() as session:
            while self.listening:
                for websocket_url in self.websocket_urls:
                    try:
                        async with session.ws_connect(websocket_url) as ws:
                            self.connection = ws
                            async for msg in self.connection:
                                if msg.type == aiohttp.WSMsgType.TEXT:
                                    await self._handle_message(json.loads(msg.data))
                                elif msg.type == aiohttp.WSMsgType.ERROR:
                                    break
                        _LOGGER.info("Home Assistant closed the websocket, retrying...")
                    except (
                        aiohttp.client_exceptions.ClientConnectorError,
                        aiohttp.client_exceptions.WSServerHandshakeError,
                        aiohttp.client_exceptions.ServerDisconnectedError,
                    ):
                        _LOGGER.info("Unable to connect to Home Assistant, retrying...")
                    await asyncio.sleep(1)

    async def query_api(self, endpoint, method="GET", decode_json=True, **params):
        """Query a Home Assistant API endpoint.

        The Home Assistant API can be queried at ``<hass url>/api/<endpoint>``. For a full reference
        of the available endpoints see https://developers.home-assistant.io/docs/en/external_api_rest.html.

        Args:
            endpoint: The endpoint that comes after /api/.
            method: HTTP method to use
            decode_json: Whether JSON should be decoded before returning
            **params: Parameters are specified as kwargs.
                      For GET requests these will be sent as url params.
                      For POST requests these will be dumped as a JSON dict and send at the post body.

        """
        url = urllib.parse.urljoin(self.api_url + "/", endpoint)
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
        }
        response = None
        _LOGGER.debug("Making a %s request to %s", method, url)
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status >= 400:
                        _LOGGER.error("Error %s - %s", resp.status, await resp.text())
                    else:
                        response = await resp.text()
            if method.upper() == "POST":
                async with session.post(
                    url, headers=headers, data=json.dumps(params)
                ) as resp:
                    if resp.status >= 400:
                        _LOGGER.error("Error %s - %s", resp.status, await resp.text())
                    else:
                        response = await resp.text()
        if decode_json and response:
            response = json.loads(response)
        return response

    async def _handle_message(self, msg):
        msg_type = msg.get("type")

        if msg_type == "auth_required":
            await self.connection.send_json(
                {"type": "auth", "access_token": self.token}
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
            try:
                event = HassEvent(raw_event=msg)
                await event.update_entity("event_type", msg["event"]["event_type"])
                await event.update_entity(
                    "entity_id", msg["event"]["data"]["entity_id"]
                )
                await event.update_entity(
                    "state", msg["event"]["data"]["new_state"]["state"]
                )
                changed = (
                    msg["event"]["data"]["old_state"] is None
                    or msg["event"]["data"]["new_state"]["state"]
                    != msg["event"]["data"]["old_state"]["state"]
                )
                await event.update_entity("changed", changed)
                await self.opsdroid.parse(event)
            except (TypeError, KeyError):
                _LOGGER.error(
                    "Home Assistant sent an event which didn't look like one we expected."
                )
                _LOGGER.error(msg)

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
        self.discovery_info = None
        self.listening = False
        await self.connection.close()
