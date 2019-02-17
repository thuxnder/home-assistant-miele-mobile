"""
Support for Miele@Home devices.
"""

import logging
import voluptuous as vol
from homeassistant.const import (
    CONF_DEVICES,
    CONF_HOST,
    CONF_TIMEOUT,
    CONF_ENTITY_ID
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.discovery import load_platform

from .MieleHomeApi import MieleHomeDevice

# requirements of MieleHomeApi
REQUIREMENTS = ['requests', 'datetime', 'cryptography']

DOMAIN = 'mielehome'
SUPPORTED_DOMAINS = ['sensor']

# DEFAULTS
DEFAULT_TIMEOUT = 30

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES):
            vol.All(cv.ensure_list, [
                vol.Schema({
                    vol.Required(CONF_HOST): cv.string,
                    vol.Required('group_id'): cv.string,
                    vol.Required('group_key'): cv.string,
                    vol.Optional(CONF_ENTITY_ID, default=''): cv.string,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.socket_timeout,
                }),
            ]),
        })
}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the Miele@Home platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # component = EntityComponent(_LOGGER, DOMAIN, hass)
    devices = [MieleHome(conf) for conf in config[DOMAIN].get(CONF_DEVICES)]
    hass.data[DOMAIN] = devices

    for supported_domain in SUPPORTED_DOMAINS:
        load_platform(hass, supported_domain, DOMAIN, {}, config)
    return True


class MieleHome(Entity):
    def __init__(self, conf):
        self._conf = conf
        device_id = conf.get(CONF_ENTITY_ID)
        self._device_id = device_id if device_id != '' else None
        host = conf.get(CONF_HOST)
        group_id = bytes.fromhex(conf.get('group_id'))
        group_key = bytes.fromhex(conf.get('group_key'))
        timeout = conf.get(CONF_TIMEOUT)
        self._device = MieleHomeDevice(host, group_id, group_key, timeout)

    def getState(self):
        return self._device.getState(self._device_id)

    def getIdent(self):
        return self._device.getIdent(self._device_id)