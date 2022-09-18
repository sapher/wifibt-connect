from asyncio.log import logger
import dbus
import functools
import dbus.service
import dbus.mainloop.glib
from ble.constants import BLUEZ_SERVICE_NAME, AGENT_MANAGER_IFACE, AGENT_IFACE

AGENT_PATH = '/test/agent'


class HeadlessAgent(dbus.service.Object):
    """
    org.bluez.Agent1 interface implementation
    """
    @dbus.service.method(AGENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        print("Release")


def register_agent_cb():
    """
    Callback for agent registration
    """
    logger.info('Agent registered')


def register_agent_error_cb(mainloop, error):
    """
    Callback for agent registration error
    """
    logger.error(f"Failed to register agent: {str(error)}")
    mainloop.quit()


def agent_main(mainloop, bus):
    """
    Headless agent main
    """
    agent = HeadlessAgent(bus, AGENT_PATH)

    manager = dbus.Interface(bus.get_object(
        BLUEZ_SERVICE_NAME, '/org/bluez'), AGENT_MANAGER_IFACE)

    logger.info('Registering agent...')
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput",
                          reply_handler=register_agent_cb,
                          error_handler=functools.partial(register_agent_error_cb, mainloop))

    logger.info('Set registered agent as default')
    manager.RequestDefaultAgent(AGENT_PATH)
