from typing import Callable

from opsdroid.matchers import match_event
from opsdroid_homeassistant.connector import HassEvent


def match_hass_state_changed(entity_id: str, **kwargs) -> Callable[Callable]:
    """Example function with PEP 484 type annotations.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.

    """
    return match_event(HassEvent, entity_id=entity_id, changed=True, **kwargs)
