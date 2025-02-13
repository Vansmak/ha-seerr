"""Support for Jellyseerr."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pyjellyseerr import JellyseerrClient, JellyseerrError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.entity_platform import async_get_platforms
from homeassistant.helpers import webhook

from .const import (
    ATTR_MEDIA_TYPE,
    ATTR_NAME,
    ATTR_SEASON,
    ATTR_STATUS,
    ATTR_TYPE,
    CONF_URLBASE,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_REQUEST_TYPE,
    DEFAULT_SEASON,
    DEFAULT_SSL,
    DEFAULT_URLBASE,
    DOMAIN,
    SERVICE_MOVIE_REQUEST,
    SERVICE_TV_REQUEST,
    SERVICE_UPDATE_STATUS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                vol.Optional(CONF_URLBASE, default=DEFAULT_URLBASE): cv.string,
                vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Jellyseerr component."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]
    
    # Create config entry from YAML configuration
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}, data=conf
        )
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jellyseerr from a config entry."""
    session = async_get_clientsession(hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, True))
    
    client = JellyseerrClient(
        host=entry.data[CONF_HOST],
        api_key=entry.data[CONF_API_KEY],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        ssl=entry.data.get(CONF_SSL, DEFAULT_SSL),
        urlbase=entry.data.get(CONF_URLBASE, DEFAULT_URLBASE),
        session=session,
    )

    try:
        await client.async_test_connection()
    except JellyseerrError as err:
        _LOGGER.error("Unable to connect to Jellyseerr: %s", err)
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_movie_request(call: ServiceCall) -> None:
        """Handle movie request service calls."""
        name = call.data[ATTR_NAME]
        request_type = call.data.get(ATTR_TYPE, DEFAULT_REQUEST_TYPE)
        
        try:
            await client.async_request_movie(name, request_type)
        except JellyseerrError as err:
            _LOGGER.error("Unable to request movie: %s", err)

    async def handle_tv_request(call: ServiceCall) -> None:
        """Handle TV request service calls."""
        name = call.data[ATTR_NAME]
        season = call.data.get(ATTR_SEASON, DEFAULT_SEASON)
        request_type = call.data.get(ATTR_TYPE, DEFAULT_REQUEST_TYPE)
        
        try:
            await client.async_request_tv(name, season, request_type)
        except JellyseerrError as err:
            _LOGGER.error("Unable to request TV show: %s", err)

    async def handle_status_update(call: ServiceCall) -> None:
        """Handle status update service calls."""
        name = call.data[ATTR_NAME]
        new_status = call.data[ATTR_STATUS]
        media_type = call.data[ATTR_MEDIA_TYPE]
        
        try:
            await client.async_update_media_status(name, media_type, new_status)
        except JellyseerrError as err:
            _LOGGER.error("Unable to update media status: %s", err)

    # Register services
    hass.services.async_register(DOMAIN, SERVICE_MOVIE_REQUEST, handle_movie_request)
    hass.services.async_register(DOMAIN, SERVICE_TV_REQUEST, handle_tv_request)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_STATUS, handle_status_update)

    # Set up webhook if API key is provided
    if CONF_API_KEY in entry.data:
        webhook_id = entry.entry_id
        
        webhook.async_register(
            hass,
            DOMAIN,
            "Jellyseerr",
            webhook_id,
            webhook.async_generate_path(webhook_id),
            webhook.async_generate_url(hass, webhook_id),
            allow_local_requests=True,
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        webhook.async_unregister(hass, entry.entry_id)
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
