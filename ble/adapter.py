from .constants import BLUEZ_SERVICE_NAME, ADAPTER_ROOT, ADAPTER_IFACE
import dbus
import logging

logger = logging.getLogger('wfbt')


class Adapter:
    def __init__(self, bus, alias=None, idx=0):
        self.path = f'{ADAPTER_ROOT}{idx}'
        self.adapter_object = bus.get_object(BLUEZ_SERVICE_NAME, self.path)
        self.adapter_props = dbus.Interface(
            self.adapter_object, dbus.PROPERTIES_IFACE)

        self.adapter_props.Set(ADAPTER_IFACE, "Powered", dbus.Boolean(1))

        if alias is not None:
            self.adapter_props.Set(ADAPTER_IFACE, 'Alias', alias)

        logger.info(f"Adapater {self.get_adapter_name()} configured...")

    def get_adapter_name(self):
        return self.path.split("/")[-1]

    def get_path(self):
        return self.path
