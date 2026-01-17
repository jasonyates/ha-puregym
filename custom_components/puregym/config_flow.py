"""Config flow for PureGym integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_PIN
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

CONF_SCAN_INTERVAL = "scan_interval"


def validate_credentials(email: str, pin: str) -> dict[str, Any]:
    """Validate credentials and return gym info."""
    from puregym_attendance import PuregymAPIClient

    client = PuregymAPIClient(email=email, pin=int(pin))
    # This will raise an exception if auth fails
    attendance = client.get_gym_attendance()
    return {
        "gym_name": getattr(client, "gym_name", "PureGym"),
        "attendance": attendance,
    }


class PuregymConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PureGym."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return PuregymOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            pin = user_input[CONF_PIN]

            await self.async_set_unique_id(email.lower())
            self._abort_if_unique_id_configured()

            try:
                info = await self.hass.async_add_executor_job(
                    validate_credentials, email, pin
                )
            except Exception:
                _LOGGER.exception("Failed to authenticate with PureGym")
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title=info.get("gym_name", "PureGym"),
                    data={
                        CONF_EMAIL: email,
                        CONF_PIN: pin,
                    },
                    options={
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PIN): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )


class PuregymOptionsFlow(OptionsFlow):
    """Handle options flow for PureGym."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): int,
                }
            ),
        )
