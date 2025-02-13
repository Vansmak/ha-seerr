"""Support for Jellyseerr and Overseerr."""
from datetime import timedelta
import logging
from typing import Any, Dict, Optional

from pyseerr import seerrError

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=300)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the seerr sensor platform."""
    seerr = hass.data[DOMAIN][config_entry.entry_id]
    sensors = []
    
    for sensor in SENSOR_TYPES:
        sensors.append(
            seerrSensor(
                sensor,
                SENSOR_TYPES[sensor]["type"],
                seerr,
                SENSOR_TYPES[sensor]["icon"],
            )
        )
    
    async_add_entities(sensors, True)

class seerrSensor(SensorEntity):
    """Representation of a seerr sensor."""

    def __init__(self, label: str, sensor_type: str, seerr: Any, icon: str) -> None:
        """Initialize the sensor."""
        self._label = label
        self._type = sensor_type
        self._seerr = seerr
        self._icon = icon
        self._attr_unique_id = f"seerr_{label}"
        self._attr_name = f"seerr {sensor_type}"
        self._attr_icon = icon
        self._attr_extra_state_attributes: Dict[str, Any] = {}
        self._attr_native_value: Optional[int] = None

    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            if self._label == "issues":
                issue_counts = await self._seerr.async_get_issue_counts()
                last_issue = await self._seerr.async_get_last_issue()
                self._attr_native_value = issue_counts.get("open", 0)
                
                # Merge issue counts with last issue details
                merged_dict = issue_counts.copy()
                if last_issue:
                    merged_dict["last_issue"] = last_issue
                self._attr_extra_state_attributes = merged_dict
                
            elif self._label == "movies":
                counts = await self._seerr.async_get_movie_requests_count()
                last_request = await self._seerr.async_get_last_movie_request()
                
                # Total count includes both standard and 4K requests
                self._attr_native_value = counts.get("total", 0)
                
                # Add detailed counts to attributes
                self._attr_extra_state_attributes = {
                    "standard_requests": counts.get("standard", 0),
                    "4k_requests": counts.get("4k", 0),
                    "pending_requests": counts.get("pending", 0),
                    "approved_requests": counts.get("approved", 0),
                    "last_request": last_request
                }
                
            elif self._label == "tv":
                counts = await self._seerr.async_get_tv_requests_count()
                last_request = await self._seerr.async_get_last_tv_request()
                
                # Total count includes both standard and 4K requests
                self._attr_native_value = counts.get("total", 0)
                
                # Add detailed counts to attributes
                self._attr_extra_state_attributes = {
                    "standard_requests": counts.get("standard", 0),
                    "4k_requests": counts.get("4k", 0),
                    "pending_requests": counts.get("pending", 0),
                    "approved_requests": counts.get("approved", 0),
                    "last_request": last_request
                }
                
            elif self._label == "pending":
                counts = await self._seerr.async_get_pending_requests_count()
                last_request = await self._seerr.async_get_last_pending_request()
                
                self._attr_native_value = counts.get("total", 0)
                
                # Add detailed counts to attributes
                self._attr_extra_state_attributes = {
                    "movies": counts.get("movies", 0),
                    "tv_shows": counts.get("tv", 0),
                    "standard_requests": counts.get("standard", 0),
                    "4k_requests": counts.get("4k", 0),
                    "last_pending_request": last_request
                }
                
            elif self._label == "total":
                counts = await self._seerr.async_get_total_requests_count()
                last_request = await self._seerr.async_get_last_request()
                
                self._attr_native_value = counts.get("total", 0)
                
                # Add detailed counts to attributes
                self._attr_extra_state_attributes = {
                    "movies": counts.get("movies", 0),
                    "tv_shows": counts.get("tv", 0),
                    "standard_requests": counts.get("standard", 0),
                    "4k_requests": counts.get("4k", 0),
                    "approved": counts.get("approved", 0),
                    "pending": counts.get("pending", 0),
                    "available": counts.get("available", 0),
                    "processing": counts.get("processing", 0),
                    "last_request": last_request
                }
                
        except seerrError as err:
            _LOGGER.warning("Unable to update seerr sensor: %s", err)
            self._attr_native_value = None
