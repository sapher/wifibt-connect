from __future__ import print_function
import functools
import logging
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from .advertising import Advertisement

from .constants import LE_ADVERTISING_MANAGER_IFACE, BLUEZ_SERVICE_NAME

logger = logging.getLogger('wfbt')


class DeviceAdvertisement(Advertisement):
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


def advertising_main(mainloop, bus, adapter):
    """
    Advertising main function
    """
    ad_manager = dbus.Interface(bus.get_object(
        BLUEZ_SERVICE_NAME, adapter.get_path()), LE_ADVERTISING_MANAGER_IFACE)

    device_advertisement = DeviceAdvertisement(bus, 0)

    ad_manager.RegisterAdvertisement(device_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=functools.partial(register_ad_error_cb, mainloop))
