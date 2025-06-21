from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
import aiohttp
import logging
from .const import TARGET_CITY, URL, HEADERS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    sensors = [
        TelMondRedAlertSensor("alert"),
        TelMondRedAlertSensor("leave"),
        TelMondRedAlertSensor("early_warning")
    ]
    async_add_entities(sensors, True)

class TelMondRedAlertSensor(Entity):
    def __init__(self, sensor_type):
        self._type = sensor_type
        self._state = None

    @property
    def name(self):
        return f"Tel Mond Red Alert {self._type.capitalize()}"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL, headers=HEADERS) as resp:
                    data = await resp.json()
            alerts = data.get("data", [])
            city_alert = any(TARGET_CITY in alert.get("cities", []) for alert in alerts)

            if self._type == "alert":
                self._state = "unsafe" if city_alert else "safe"
            elif self._type == "leave":
                self._state = "false" if city_alert else "true"
            elif self._type == "early_warning":
                self._state = "unsafe" if city_alert else "safe"

        except Exception as e:
            _LOGGER.error(f"Tel Mond Red Alert sensor update failed: {e}")
            self._state = None
