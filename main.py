#!/usr/bin/env python
import signal
import dbus
from gi.repository import GLib
import log
from ble.advertising_main import advertising_main
from ble.gatt_server_main import gatt_server_main


def bootstrap():
    """
    Entry point bootstrap function
    """
    logger = log.setup_custom_logger('wfbt')
    logger.info('wfbt started')

    # GLib main loop configuration
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    loop = GLib.MainLoop()

    # Setup BLE services
    adapter_name = ""
    advertising_main(loop, bus, adapter_name)
    gatt_server_main(loop, bus, adapter_name)

    # Trap sigint signal for program termination
    def ex(_sig, _frame):
        loop.quit()
    signal.signal(signal.SIGINT, ex)

    loop.run()


if __name__ == "__main__":
    bootstrap()
