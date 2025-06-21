from homeassistant.helpers.entity_platform import async_generate_entity_id
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

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
        self.entity_id = async_generate_entity_id(
            "sensor.tel_mond_red_alert_{}", sensor_type, hass=hass
        )

    @property
    def name(self):
        return f"Tel Mond Red Alert {self._type.capitalize()}"

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # async friendly update with aiohttp, example below
        import aiohttp
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
