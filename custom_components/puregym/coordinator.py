"""DataUpdateCoordinator for PureGym."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"


class PuregymDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching PureGym data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._email = entry.data[CONF_EMAIL]
        self._pin = entry.data[CONF_PIN]
        self._client = None
        self.gym_name: str | None = None

        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    def _get_client(self):
        """Get or create the PureGym client."""
        if self._client is None:
            from puregym_attendance import PuregymAPIClient

            self._client = PuregymAPIClient(email=self._email, pin=self._pin)
        return self._client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from PureGym API."""
        try:
            client = await self.hass.async_add_executor_job(self._get_client)
            attendance = await self.hass.async_add_executor_job(
                client.get_gym_attendance
            )

            # Try to get gym name if available
            if self.gym_name is None:
                self.gym_name = getattr(client, "gym_name", None)

            return {
                "attendance": attendance,
                "gym_name": self.gym_name,
            }
        except Exception as err:
            _LOGGER.warning("Failed to fetch PureGym data: %s", err)
            raise UpdateFailed(f"Failed to fetch data: {err}") from err
