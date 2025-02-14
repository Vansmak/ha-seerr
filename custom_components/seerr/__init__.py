# __init__.py
"""Support for Seerr."""
import logging

import pyoverseerr
import voluptuous as vol
import asyncio
import json

from datetime import timedelta

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_API_KEY,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL,
)
import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.event import track_time_interval

from .const import (
    ATTR_MEDIA_TYPE,
    ATTR_NAME,
    ATTR_SEASON,
    ATTR_STATUS,
    CONF_URLBASE,
    DEFAULT_PORT,
    DEFAULT_SEASON,
    DEFAULT_SSL,
    DEFAULT_URLBASE,
    DOMAIN,
    SERVICE_MOVIE_REQUEST,
    SERVICE_MUSIC_REQUEST,
    SERVICE_TV_REQUEST,
    SERVICE_UPDATE_STATUS,
)

DEPENDENCIES = ['webhook']
_LOGGER = logging.getLogger(__name__)
EVENT_RECEIVED = "SEERR_EVENT"

def urlbase(value) -> str:
    """Validate and transform urlbase."""
    if value is None:
        raise vol.Invalid("string value is None")
    value = str(value).strip("/")
    if not value:
        return value
    return f"{value}/"

SUBMIT_MOVIE_REQUEST_SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string})

SUBMIT_MUSIC_REQUEST_SERVICE_SCHEMA = vol.Schema({vol.Required(ATTR_NAME): cv.string})

SUBMIT_TV_REQUEST_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_SEASON, default=DEFAULT_SEASON): vol.In(
            ["first", "latest", "all"]
        ),
    }
)

SERVICE_UPDATE_STATUS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_STATUS): cv.string,
        vol.Required(ATTR_MEDIA_TYPE): vol.In(["movie", "tv"]),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_USERNAME): cv.string,
                vol.Required(CONF_API_KEY, "auth"): cv.string,
                vol.Optional(CONF_PASSWORD, "auth"): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_URLBASE, default=DEFAULT_URLBASE): urlbase,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                vol.Optional(CONF_SCAN_INTERVAL, default=timedelta(seconds=60)): cv.time_period,
            },
            cv.has_at_least_one_key("auth"),
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up the Seerr component platform."""
    seerr = pyoverseerr.Overseerr(
        ssl=config[DOMAIN][CONF_SSL],
        host=config[DOMAIN][CONF_HOST],
        port=config[DOMAIN][CONF_PORT],
        urlbase=config[DOMAIN][CONF_URLBASE],
        username=config[DOMAIN].get(CONF_USERNAME),
        password=config[DOMAIN].get(CONF_PASSWORD),
        api_key=config[DOMAIN].get(CONF_API_KEY),
    )

    scan_interval=config[DOMAIN][CONF_SCAN_INTERVAL]

    try:
        seerr.authenticate()
        seerr.test_connection()
    except pyoverseerr.OverseerrError as err:
        _LOGGER.warning("Unable to setup Seerr: %s", err)
        return False

    hass.data[DOMAIN] = {"instance": seerr}

    def submit_movie_request(call):
        """Submit request for movie."""
        name = call.data[ATTR_NAME]
        movies = seerr.search_movie(name)["results"]
        if movies:
            movie = movies[0]
            seerr.request_movie(movie["id"])
        else:
            raise Warning("No movie found.")

    def submit_tv_request(call):
        """Submit request for TV show."""
        name = call.data[ATTR_NAME]
        tv_shows = seerr.search_tv(name)["results"]

        if tv_shows:
            season = call.data[ATTR_SEASON]
            show = tv_shows[0]["id"]
            if season == "first":
                seerr.request_tv(show, request_first=True)
            elif season == "latest":
                seerr.request_tv(show, request_latest=True)
            elif season == "all":
                seerr.request_tv(show, request_all=True)
        else:
            raise Warning("No TV show found.")

    def submit_music_request(call):
        """Submit request for music album."""
        name = call.data[ATTR_NAME]
        music = seerr.search_music_album(name)
        if music:
            seerr.request_music(music[0]["foreignAlbumId"])
        else:
            raise Warning("No music album found.")

    def update_media_status(call):
        """Update status of media by name."""
        name = call.data[ATTR_NAME]
        new_status = call.data[ATTR_STATUS]
        media_type = call.data[ATTR_MEDIA_TYPE]
        
        try:
            # Search for the media
            if media_type == "movie":
                results = seerr.search_movie(name)["results"]
            else:  # tv
                results = seerr.search_tv(name)["results"]
                
            if not results:
                _LOGGER.error("No media found with name: %s", name)
                return
                
            # Get the first matching result
            media = results[0]
            
            # Get all requests to find the matching one
            requests = seerr.get_requests()
            matching_request = None
            
            for request in requests:
                if request["media"]["tmdbId"] == media["id"]:
                    matching_request = request
                    break
                    
            if matching_request:
                seerr.update_request(matching_request["id"], new_status)
                _LOGGER.info("Updated status of %s to %s", name, new_status)
            else:
                _LOGGER.error("No request found for: %s", name)
                
        except pyoverseerr.OverseerrError as err:
            _LOGGER.error("Error updating request: %s", err)

    async def update_sensors(event_time):
        """Call to update sensors."""
        _LOGGER.debug("Updating sensors")
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_pending_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_movie_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_tv_show_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_issues"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_total_requests"]}, blocking=False)

    hass.services.register(
        DOMAIN,
        SERVICE_MOVIE_REQUEST,
        submit_movie_request,
        schema=SUBMIT_MOVIE_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_MUSIC_REQUEST,
        submit_music_request,
        schema=SUBMIT_MUSIC_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_TV_REQUEST,
        submit_tv_request,
        schema=SUBMIT_TV_REQUEST_SERVICE_SCHEMA,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_UPDATE_STATUS,
        update_media_status,
        schema=SERVICE_UPDATE_STATUS_SCHEMA,
    )
    
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)
 
    webhook_id = config[DOMAIN].get(CONF_API_KEY)
    _LOGGER.debug("webhook_id: %s", webhook_id)

    _LOGGER.info("Seerr Installing Webhook")

    hass.components.webhook.async_register(DOMAIN, "Seerr", webhook_id, handle_webhook)

    url = hass.components.webhook.async_generate_url(webhook_id)
    _LOGGER.debug("webhook data: %s", url)

    track_time_interval(hass, update_sensors, scan_interval)

    return True

async def handle_webhook(hass, webhook_id, request):
    """Handle webhook callback."""
    _LOGGER.info("webhook called")

    body = await request.text()
    try:
        data = json.loads(body) if body else {}
    except ValueError:
        return None
    _LOGGER.info("webhook data: %s", body)

    published_data = data
    _LOGGER.info("webhook data: %s", published_data)
    try:
        if data['notification_type'] == 'MEDIA_PENDING':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_pending_requests"]}, blocking=True)
        if data['media']['media_type'] == 'movie':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_movie_requests"]}, blocking=True)
        if data['media']['media_type'] == 'tv':
            await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_tv_show_requests"]}, blocking=True)
        await hass.services.async_call("homeassistant", "update_entity", {ATTR_ENTITY_ID: ["sensor.seerr_total_requests"]}, blocking=False)

    except Exception:
        pass

    hass.bus.async_fire(EVENT_RECEIVED, published_data)
