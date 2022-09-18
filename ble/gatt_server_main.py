from __future__ import print_function
import functools
import logging
import dbus
import dbus.exceptions
from ble.service_network import NetworkService
from .constants import BLUEZ_SERVICE_NAME, DBUS_OM_IFACE, GATT_MANAGER_IFACE

logger = logging.getLogger('wfbt')


class Application(dbus.service.Object):
    """
    org.bluez.GattApplication1 interface implementation
    """

    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

        # Register network ble service
        self.add_service(NetworkService(bus, 0))

    def get_path(self):
        """
        Get path
        """
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        """
        Add service to list services
        """
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        """
        Get managed objects
        """
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                descs = chrc.get_descriptors()
                for desc in descs:
                    response[desc.get_path()] = desc.get_properties()

        return response


def register_app_cb():
    """
    Callback for application registration
    """
    logger.info('GATT application registered')


def register_app_error_cb(mainloop, error):
    """
    Callback for application registration error
    """
    logger.error(f"Failed to register application: {str(error)}")
    mainloop.quit()


def gatt_server_main(mainloop, bus, adapter):
    """
    GATT server main
    """
    service_manager = dbus.Interface(
        bus.get_object(BLUEZ_SERVICE_NAME, adapter.get_path()),
        GATT_MANAGER_IFACE)

    app = Application(bus)

    logger.info('Registering GATT application...')

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=functools.partial(register_app_error_cb, mainloop))
