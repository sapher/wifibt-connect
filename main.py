#!/usr/bin/env python3
import signal
import dbus
from gi.repository import GLib
import log
from ble.adapter import Adapter
from ble.advertising_main import advertising_main
from ble.gatt_server_main import gatt_server_main
from ble.agent_main import agent_main
import os

if __name__ == "__main__":
    logger = log.setup_custom_logger('wfbt')
    logger.info('wfbt started')

    # GLib main loop configuration
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    loop = GLib.MainLoop()

    # Setup adapter
    adapter_alias = os.getenv("ADAPTER_ALIAS")
    adapter = Adapter(bus, adapter_alias)

    # Setup BLE services
    advertising_main(loop, bus, adapter)
    gatt_server_main(loop, bus, adapter)
    agent_main(loop, bus)

    # Trap sigint signal for program termination
    def ex(_sig, _frame):
        adapter.disable_adapter()
        loop.quit()
    signal.signal(signal.SIGINT, ex)

    loop.run()
