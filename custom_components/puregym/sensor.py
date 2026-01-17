"""Sensor platform for PureGym integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PuregymDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PureGym sensor from a config entry."""
    coordinator: PuregymDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PuregymAttendanceSensor(coordinator, entry)])


class PuregymAttendanceSensor(CoordinatorEntity[PuregymDataUpdateCoordinator], SensorEntity):
    """Sensor showing current gym attendance."""

    _attr_has_entity_name = True
    _attr_name = "Attendance"
    _attr_native_unit_of_measurement = "people"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:account-group"

    def __init__(
        self,
        coordinator: PuregymDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_attendance"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": coordinator.gym_name or "PureGym",
            "manufacturer": "PureGym",
        }

    @property
    def native_value(self) -> int | None:
        """Return the current attendance."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("attendance")

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return additional state attributes."""
        attrs = {}
        if self.coordinator.data:
            attrs["gym_name"] = self.coordinator.data.get("gym_name")
        if self.coordinator.last_update_success_time:
            attrs["last_updated"] = self.coordinator.last_update_success_time.isoformat()
        return attrs
