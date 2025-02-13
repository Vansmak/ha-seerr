"""Support for Jellyseerr."""
from datetime import timedelta
import logging
from typing import Any, Dict, Optional

from pyjellyseerr import JellyseerrError

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)  # Reduced from 86400 for more responsive updates

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jellyseerr sensor platform."""
    jellyseerr = hass.data[DOMAIN][config_entry.entry_id]
    sensors = []
    
    for sensor in SENSOR_TYPES:
        sensors.append(
            JellyseerrSensor(
                sensor,
                SENSOR_TYPES[sensor]["type"],
                jellyseerr,
                SENSOR_TYPES[sensor]["icon"],
            )
        )
    
    async_add_entities(sensors, True)

class JellyseerrSensor(SensorEntity):
    """Representation of a Jellyseerr sensor."""

    def __init__(self, label: str, sensor_type: str, jellyseerr: Any, icon: str) -> None:
        """Initialize the sensor."""
        self._label = label
        self._type = sensor_type
        self._jellyseerr = jellyseerr
        self._icon = icon
        self._attr_name = f"Jellyseerr {sensor_type}"
        self._attr_icon = icon
        self._attr_extra_state_attributes: Dict[str, Any] = {}
        self._attr_state: Optional[int] = None

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            if self._label == "issues":
                issue_counts = await self._jellyseerr.async_get_issue_counts()
                last_issue = await self._jellyseerr.async_get_last_issue()
                self._attr_state = issue_counts.get("open", 0)
                
                merged_dict = issue_counts.copy()
                if last_issue:
                    merged_dict.update(last_issue)
                self._attr_extra_state_attributes = merged_dict
                
            elif self._label == "movies":
                self._attr_state = await self._jellyseerr.async_get_movie_requests_count()
                self._attr_extra_state_attributes = await self._jellyseerr.async_get_last_movie_request()
                
            elif self._label == "tv":
                self._attr_state = await self._jellyseerr.async_get_tv_requests_count()
                self._attr_extra_state_attributes = await self._jellyseerr.async_get_last_tv_request()
                
            elif self._label == "pending":
                self._attr_state = await self._jellyseerr.async_get_pending_requests_count()
                self._attr_extra_state_attributes = await self._jellyseerr.async_get_last_pending_request()
                
            elif self._label == "total":
                self._attr_state = await self._jellyseerr.async_get_total_requests_count()
                self._attr_extra_state_attributes = await self._jellyseerr.async_get_last_request()
                
        except JellyseerrError as err:
            _LOGGER.warning("Unable to update Jellyseerr sensor: %s", err)
            self._attr_state = None
