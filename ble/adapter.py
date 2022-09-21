import logging
import dbus
from .constants import BLUEZ_SERVICE_NAME, ADAPTER_ROOT, ADAPTER_IFACE

logger = logging.getLogger('wfbt')


class Adapter:
    """
    Adapter implementation
    """

    def __init__(self, bus, alias=None, idx=0):
        self.path = f'{ADAPTER_ROOT}{idx}'
        self.adapter_object = bus.get_object(BLUEZ_SERVICE_NAME, self.path)
        self.adapter_props = dbus.Interface(
            self.adapter_object, dbus.PROPERTIES_IFACE)

        logger.info(f"Start configuration of interface: {self.path}")

        self.enable_adapter()

        if alias is not None:
            self.adapter_props.Set(ADAPTER_IFACE, 'Alias', alias)

        logger.info(f"Adapater {self.get_adapter_name()} configured...")

    def get_adapter_name(self):
        """
        Get adapeter name
        """
        return self.path.split("/")[-1]

    def get_path(self):
        """
        Get path
        """
        return self.path

    def enable_adapter(self):
        """
        Enable adapter by turning it on, make it discoverable and pairable
        """
        logger.info(f"enable adapter {self.path}")
        self.set_adapter_prop(ADAPTER_IFACE, "Powered", dbus.Boolean(1))
        self.set_adapter_prop(ADAPTER_IFACE, "Discoverable", dbus.Boolean(1))
        self.set_adapter_prop(ADAPTER_IFACE, "Pairable", dbus.Boolean(1))

    def disable_adapter(self, shutdown=False):
        """
        Disable by stopping discoverable and pairable
        Optionally shutdown the device
        """
        logger.info(f"disable adapter {self.path}")
        self.set_adapter_prop(ADAPTER_IFACE, "Discoverable", dbus.Boolean(0))
        self.set_adapter_prop(ADAPTER_IFACE, "Pairable", dbus.Boolean(0))
        if (shutdown):
            self.set_adapter_prop(ADAPTER_IFACE, "Powered", dbus.Boolean(0))

    def set_adapter_prop(self, adapter_iface, key, value):
        """
        Set property on adapter

        :adapter_iface : Adapter interface name
        :key : property name
        :value : property value
        """
        logger.debug(f"set adapter {adapter_iface} property {key} to value {value}")
        self.adapter_props.Set(adapter_iface, key, value)