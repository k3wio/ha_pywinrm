"""Support for winrm commands to turn a switch on/off."""
import logging

import winrm

import voluptuous as vol

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchDevice,
)
from homeassistant.const import (
    CONF_COMMAND_OFF,
    CONF_COMMAND_ON,
    CONF_COMMAND_STATE,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_FRIENDLY_NAME,
    CONF_SWITCHES,
    CONF_USERNAME,
    CONF_VALUE_TEMPLATE,
)
from .const import DOMAIN
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_COMMAND_OFF, default="true"): cv.string,
        vol.Optional(CONF_COMMAND_ON, default="true"): cv.string,
        vol.Optional(CONF_COMMAND_STATE): cv.string,
        vol.Optional(CONF_FRIENDLY_NAME): cv.string,
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_SWITCHES): cv.schema_with_slug_keys(SWITCH_SCHEMA)}
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Find and return switches controlled by shell commands."""
    devices = config.get(CONF_SWITCHES, {})
    switches = []

    for object_id, device_config in devices.items():
        value_template = device_config.get(CONF_VALUE_TEMPLATE)

        if value_template is not None:
            value_template.hass = hass

        switches.append(
            CommandSwitch(
                hass,
                object_id,
                device_config.get(CONF_FRIENDLY_NAME, object_id),
                device_config.get(CONF_COMMAND_ON),
                device_config.get(CONF_COMMAND_OFF),
                device_config.get(CONF_COMMAND_STATE),
                device_config.get(CONF_HOST),
                device_config.get(CONF_PASSWORD),
                device_config.get(CONF_USERNAME),
                value_template,
            )
        )

    if not switches:
        _LOGGER.error("No switches added")
        return False

    add_entities(switches)


class CommandSwitch(SwitchDevice):
    """Representation a switch that can be toggled using shell commands."""

    def __init__(
        self,
        hass,
        object_id,
        friendly_name,
        command_on,
        command_off,
        command_state,
        host,
        password,
        username,
        value_template,
    ):
        """Initialize the switch."""
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._name = friendly_name
        self._state = False
        self._command_on = command_on
        self._command_off = command_off
        self._command_state = command_state
        self._host = host
        self._password = password
        self._username = username
        self._value_template = value_template

    @staticmethod
    def _switch(command, host, password, username):
        """Execute the actual commands."""
        _LOGGER.info("Running command: %s on host: %s" % (command, host))

        try:
            session = winrm.Session(host, auth=(username, password))
            response_object = session.run_ps(command)
            success = response_object.status_code == 0
        except Exception as e:
            _LOGGER.error("Command failed: %s on host: %s. %s" % (command, host, e))
            _LOGGER.error("  %s" % (e))

        if not success:
            _LOGGER.error("Command failed: %s on host: %s" % (command, host))

        return success

    @staticmethod
    def _query_state_value(command, host, password, username):
        """Execute state command for return value."""
        _LOGGER.info("Running state command: %s on host: %s" % (command, host))

        try:
            session = winrm.Session(host, auth=(username, password))
            response_object = session.run_ps(command)
            std_out = response_object.std_out.strip().decode("utf-8")
            std_err = response_object.std_err.strip().decode("utf-8")
            status_code = response_object.status_code
            return std_out
        except Exception as e:
            _LOGGER.error("State command failed: %s on host: %s. %s" % (command, host, e))

    @staticmethod
    def _query_state_code(command, host, password, username):
        """Execute state command for return code."""
        _LOGGER.info("Running state command: %s on host: %s" % (command, host))
        try:
            session = winrm.Session(host, auth=(username, password))
            response_object = session.run_ps(command)
            status_code = response_object.status_code
            return status_code
        except Exception as e:
            _LOGGER.error("State command failed: %s on host: %s. %s" % (command, host, e))

    @property
    def should_poll(self):
        """Only poll if we have state command."""
        return self._command_state is not None

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @property
    def assumed_state(self):
        """Return true if we do optimistic updates."""
        return self._command_state is None

    def _query_state(self):
        """Query for state."""
        if not self._command_state:
            _LOGGER.error("No state command specified")
            return
        if self._value_template:
            return CommandSwitch._query_state_value(
                self._command_state, self._host, self._password, self._username,
            )
        return CommandSwitch._query_state_code(
            self._command_state, self._host, self._password, self._username,
        )

    def update(self):
        """Update device state."""
        if self._command_state:
            payload = str(self._query_state())
            if self._value_template:
                payload = self._value_template.render_with_possible_json_value(payload)
            self._state = payload.lower() == "true"

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if (
            CommandSwitch._switch(
                self._command_on, self._host, self._password, self._username
            )
            and not self._command_state
        ):
            self._state = True
            self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if (
            CommandSwitch._switch(
                self._command_off, self._host, self._password, self._username
            )
            and not self._command_state
        ):
            self._state = False
            self.schedule_update_ha_state()
