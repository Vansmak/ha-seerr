"""Support for Jellyseerr."""
from typing import Final

ATTR_NAME: Final = "name"
ATTR_SEASON: Final = "season"
ATTR_TYPE: Final = "type"
ATTR_STATUS: Final = "new_status"
ATTR_MEDIA_TYPE: Final = "type"

CONF_URLBASE: Final = "urlbase"
DEFAULT_NAME = DOMAIN = "jellyseerr"
DEFAULT_PORT: Final = 5055
DEFAULT_SEASON: Final = "latest"
DEFAULT_SSL: Final = False
DEFAULT_URLBASE: Final = ""
DEFAULT_REQUEST_TYPE: Final = "standard"

SERVICE_MOVIE_REQUEST: Final = "submit_movie_request"
SERVICE_TV_REQUEST: Final = "submit_tv_request"
SERVICE_UPDATE_STATUS: Final = "update_media_status"

SENSOR_TYPES: Final = {
    "movies": {"type": "Movie requests", "icon": "mdi:movie"},
    "tv": {"type": "TV Show requests", "icon": "mdi:television-classic"},
    "pending": {"type": "Pending requests", "icon": "mdi:clock-alert-outline"},
    "total": {"type": "Total requests", "icon": "mdi:movie"},
    "issues": {"type": "Issues", "icon": "mdi:alert-circle-outline"},
}
