from __future__ import print_function
import functools
import logging
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from .advertising import Advertisement

from .constants import LE_ADVERTISING_MANAGER_IFACE, BLUEZ_SERVICE_NAME, DBUS_PROP_IFACE
from . import adapters

logger = logging.getLogger('wfbt')


class TestAdvertisement(Advertisement):
    """
    Advertisement class
    """

    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
        self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.include_tx_power = True


def register_ad_cb():
    """
    Advertisement register callback
    """
    logger.info('Advertisement registered')


def register_ad_error_cb(mainloop, error):
    """
    Advertisement register error callback
    """
    logger.error(f"Failed to register advertisement: {str(error)}")
    mainloop.quit()


def advertising_main(mainloop, bus, adapter_name):
    """
    Advertising main function
    """
    adapter = adapters.find_adapter(
        bus, LE_ADVERTISING_MANAGER_IFACE, adapter_name)
    logger.info(f"adapter: {adapter}")
    if not adapter:
        raise Exception('LEAdvertisingManager1 interface not found')

    adapter_props = dbus.Interface(bus.get_object(
        BLUEZ_SERVICE_NAME, adapter), DBUS_PROP_IFACE)

    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    ad_manager = dbus.Interface(bus.get_object(
        BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE)

    test_advertisement = TestAdvertisement(bus, 0)

    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=functools.partial(register_ad_error_cb, mainloop))
