from custom_components.mielehome import DOMAIN
from homeassistant.helpers.entity import Entity

# Dependencies
DEPENDENCIES = ['mielehome']

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Initialize the Miele@Home device."""
    sensors = [MieleSensor(device, 'Status') for device in hass.data[DOMAIN]]
    async_add_devices(sensors, update_before_add=True)


class MieleSensor(Entity):
    def __init__(self, device, key):
        self._device = device
        self._key = key
        self.__ident = {}
        self.__state = {}
        self.update_ident()
        self.update()

    @property
    def device_id(self):
        """Return the unique ID for this device."""
        return self.__ident['DeviceIdentLabel']['FabNumber']

    @property
    def unique_id(self):
        """Return the unique ID for this sensor."""
        return self.device_id + '_' + self._key

    @property
    def name(self):
        """Return the name of the sensor."""
        ident = self.__ident
        
        result = ident['DeviceName']
        if len(result) == 0:
            return ident['DeviceIdentLabel']['TechType'] + ' ' + self._key
        else:
            return result + ' ' + self._key

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.__state[self._key]

    @property    
    def device_state_attributes(self):
        return self.__state
        
    def update_ident(self):
        self.__ident = self._device.getIdent().toDict()

    def update(self):
        self.__state = self._device.getState().toDict()
        