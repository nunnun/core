"""Test the Nina init file."""
import json
from typing import Any, Dict
from unittest.mock import patch

from pynina import ApiError

from homeassistant.components.nina.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, load_fixture

ENTRY_DATA: Dict[str, Any] = {
    "slots": 5,
    "corona_filter": True,
    "regions": {"083350000000": "Aach, Stadt"},
}


async def init_integration(hass) -> MockConfigEntry:
    """Set up the NINA integration in Home Assistant."""

    dummy_response: Dict[str, Any] = json.loads(
        load_fixture("sample_warnings.json", "nina")
    )

    with patch(
        "pynina.baseApi.BaseAPI._makeRequest",
        return_value=dummy_response,
    ):

        entry: MockConfigEntry = MockConfigEntry(
            domain=DOMAIN, title="NINA", data=ENTRY_DATA
        )
        entry.add_to_hass(hass)

        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()
        return entry


async def test_config_entry_not_ready(hass: HomeAssistant) -> None:
    """Test the configuration entry."""
    entry: MockConfigEntry = await init_integration(hass)

    assert entry.state == ConfigEntryState.LOADED


async def test_sensors_connection_error(hass: HomeAssistant) -> None:
    """Test the creation and values of the NINA sensors with no connected."""
    with patch(
        "pynina.baseApi.BaseAPI._makeRequest",
        side_effect=ApiError("Could not connect to Api"),
    ):
        conf_entry: MockConfigEntry = MockConfigEntry(
            domain=DOMAIN, title="NINA", data=ENTRY_DATA
        )

        conf_entry.add_to_hass(hass)

        await hass.config_entries.async_setup(conf_entry.entry_id)
        await hass.async_block_till_done()

        assert conf_entry.state == ConfigEntryState.SETUP_RETRY
