import requests
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, TARGET_CITY, URL, HEADERS

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    sensors = [
        TelMondRedAlertSensor("alert"),
        TelMondRedAlertSensor("leave"),
        TelMondRedAlertSensor("early_warning")
    ]
    async_add_entities(sensors, True)

class TelMondRedAlertSensor(SensorEntity):
    def __init__(self, sensor_type):
        self._attr_name = f"Tel_Mond_Red_Alert_{sensor_type.capitalize()}"
        self._state = None
        self._type = sensor_type

    def update(self):
        try:
            response = requests.get(URL, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8-sig'
            data = response.json()
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

    @property
    def state(self):
        return self._state
