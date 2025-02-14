# sensor.py
"""Support for Seerr."""
from datetime import timedelta
import logging

from pyoverseerr import OverseerrError

from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=86400)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Seerr sensor platform."""
    if discovery_info is None:
        return

    sensors = []

    seerr = hass.data[DOMAIN]["instance"]

    for sensor in SENSOR_TYPES:
        sensor_label = sensor
        sensor_type = SENSOR_TYPES[sensor]["type"]
        sensor_icon = SENSOR_TYPES[sensor]["icon"]
        sensors.append(SeerrSensor(
            sensor_label, sensor_type, seerr, sensor_icon))

    add_entities(sensors, True)

class SeerrSensor(Entity):
    """Representation of a Seerr sensor."""

    def __init__(self, label, sensor_type, seerr, icon):
        """Initialize the sensor."""
        self._state = None
        self._label = label
        self._type = sensor_type
        self._seerr = seerr
        self._icon = icon
        self._last_request = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Seerr {self._type}"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Attributes."""
        return self._last_request

    def update(self):
        """Update the sensor."""
        _LOGGER.debug("Update Seerr sensor: %s", self.name)
        try:
            if self._label == "issues":
                issueCounts = self._seerr.issueCounts
                lastIssue = self._seerr.last_issue
                self._state = issueCounts["open"]
                merged_dict = issueCounts
                if (lastIssue is not None):
                    for key in lastIssue:
                        merged_dict[key] = lastIssue[key]
                self._last_request = merged_dict

            if self._label == "movies":
                self._state = self._seerr.movie_requests
                self._last_request = self._seerr.last_movie_request
            elif self._label == "total":
                self._state = self._seerr.total_requests
                self._last_request = self._seerr.last_total_request
            elif self._label == "tv":
                self._state = self._seerr.tv_requests
                self._last_request = self._seerr.last_tv_request
            elif self._label == "music":
                self._state = self._seerr.music_requests
                self._last_request = "Not Supported"
            elif self._label == "pending":
                self._state = self._seerr.pending_requests
                self._last_request = self._seerr.last_pending_request
            elif self._label == "approved":
                self._state = self._seerr.approved_requests
            elif self._label == "available":
                self._state = self._seerr.available_requests
        except OverseerrError as err:
            _LOGGER.warning("Unable to update Seerr sensor: %s", err)
            self._state = None
