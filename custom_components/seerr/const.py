ATTR_NAME = "name"
ATTR_SEASON = "season"
ATTR_STATUS = "new_status"
ATTR_MEDIA_TYPE = "type"

CONF_URLBASE = "urlbase"

DEFAULT_NAME = DOMAIN = "seerr"
DEFAULT_PORT = 5055
DEFAULT_SEASON = "latest"
DEFAULT_SSL = False
DEFAULT_URLBASE = ""

SERVICE_MOVIE_REQUEST = "submit_movie_request"
SERVICE_MUSIC_REQUEST = "submit_music_request"
SERVICE_TV_REQUEST = "submit_tv_request"
SERVICE_UPDATE_STATUS = "update_media_status"

SENSOR_TYPES = {
    "movies": {"type": "Movie requests", "icon": "mdi:movie"},
    "tv": {"type": "TV Show requests", "icon": "mdi:television-classic"},
    "pending": {"type": "Pending requests", "icon": "mdi:clock-alert-outline"},
    "total": {"type": "Total requests", "icon": "mdi:movie"},
    "issues": {"type":"Issues", "icon": "mdi:movie"},
}
