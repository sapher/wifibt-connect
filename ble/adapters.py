from __future__ import print_function
import logging
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
from .constants import BLUEZ_SERVICE_NAME, DBUS_OM_IFACE

logger = logging.getLogger('wfbt')


def find_adapter(bus, adapter_interface_name, adapter_name):
    """
    Find bluetooth adapter
    """
    remote_om = dbus.Interface(bus.get_object(
        BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        # print('checking adapter %s, keys: %s' % (o, props.keys()))
        logger.debug('checking adapter %s' % (o,))
        if adapter_interface_name in props.keys():
            logger.debug('found adapter %s' % (o,))
            if '/' + adapter_name in o:
                logger.debug('returning adapter %s' % (o,))
                return o

    return None
