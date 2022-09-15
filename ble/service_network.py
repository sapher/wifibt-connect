import urllib.parse
import logging
import functools
import dbus
from gi.repository import GObject
from NetworkManager import const, NetworkManager
from ble.exceptions import InvalidArgsException
from .dbus import utility as dbus_util
from .nm import utility as nm_util
from .constants import GATT_CHRC_IFACE
from .gatt_server import Service, Characteristic, Descriptor

logger = logging.getLogger('wfbt')


def deep_get(dictionary, keys, default=None):
    """
    Retrieve value by key in deep object
    """
    return functools.reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split('.'), dictionary)


class NetworkService(Service):
    """
    BLE Network configurator service
    """
    NETWORK_SVC_UUID = '22345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.NETWORK_SVC_UUID, True)

        logger.info(
            f'initialize NM service: {self.NETWORK_SVC_UUID}')

        NETWORK_MANAGER_DEVICE_WIFI_STATE_CHRC_UUID = '32345678-1234-5678-1234-56781abcdee2'
        NETWORK_MANAGER_DEVICE_ETHERNET_STATE_CHRC_UUID = '42345678-1234-5678-1234-56781abcdee2'

        self.add_characteristic(
            NetworkManagerStateCharacteristic(bus, 1, self))
        self.add_characteristic(
            NetworkWirelessConfigurationCharacteristic(bus, 2, self))
        self.add_characteristic(
            NetworkManagerDeviceStateCharacteristic(bus, 3, self, NETWORK_MANAGER_DEVICE_ETHERNET_STATE_CHRC_UUID, "ethernet"))
        self.add_characteristic(
            NetworkManagerDeviceStateCharacteristic(bus, 4, self, NETWORK_MANAGER_DEVICE_WIFI_STATE_CHRC_UUID, "wifi"))


class NetworkManagerDeviceStateCharacteristic(Characteristic):
    """
    Device state characteristic
    """

    def __init__(self, bus, index, service, uuid, device_type):  # pylint: disable=too-many-arguments
        Characteristic.__init__(
            self, bus, index,
            uuid,
            ['read', 'notify'],
            service)

        logger.info(
            f'initialize NM {device_type} device state characteristic: {uuid}')

        # Add descriptors
        CONN_TYPE_DESC_UUID = '72345678-1234-5678-1234-56789abcdef2'
        CONN_ID_DESC_UUID = '72345678-1234-5678-1234-56789abcdef3'
        CONN_UUID_DESC_UUID = '72345678-1234-5678-1234-56789abcdef4'
        self.add_descriptor(
            NetworkManagerDeviceActiveConnectionDescriptor(bus, 0, CONN_TYPE_DESC_UUID, self, device_type, 'connection.type'))
        self.add_descriptor(
            NetworkManagerDeviceActiveConnectionDescriptor(bus, 1, CONN_ID_DESC_UUID, self, device_type, 'connection.id'))
        self.add_descriptor(
            NetworkManagerDeviceActiveConnectionDescriptor(bus, 2, CONN_UUID_DESC_UUID, self, device_type, 'connection.uuid'))

        # initialize value
        self.device_type = device_type
        self.notifying = False
        self.value = self.read_network_manager_device_state()
        GObject.timeout_add(5000, self.notify_network_manager_device_state)

    def read_network_manager_device_state(self):
        """
        Read network manager device state
        """
        device = nm_util.get_current_device(self.device_type)
        if device is None:
            return []

        return [device.StateReason[0], device.StateReason[1]]

    def notify_network_manager_device_state(self):
        """
        Notify network manager device state
        """
        if self.notifying:
            new_value = self.read_network_manager_device_state()
            logger.debug(
                f'notify NM device {self.device_type} state {repr(new_value)}')
            self.value = new_value

            # Notify only if value exist
            if len(new_value) == 2:
                # TODO: Find a better way
                self.PropertiesChanged(
                    GATT_CHRC_IFACE, {'Value': [
                        dbus.Byte(new_value[0]),
                        dbus.Byte(new_value[1]),
                    ]}, [])
        return True

    def ReadValue(self, _options):
        """
        Read value
        """
        self.value = self.read_network_manager_device_state()
        logger.info(f"read NM device state: {repr(self.value)}")
        return self.value

    def StartNotify(self):
        """
        Start notifying
        """
        logger.info(
            f'start notifying NM device {self.device_type} state')
        if not self.notifying:
            self.notifying = True
            self.notify_network_manager_device_state()

    def StopNotify(self):
        """
        Stop notifying
        """
        logger.info(
            f'stop notifying NM device {self.device_type} state')
        if self.notifying:
            self.notifying = False


class NetworkManagerDeviceActiveConnectionDescriptor(Descriptor):
    """
    Device active connection descriptor
    """

    def __init__(self, bus, index: int, uuid: str, characteristic: Characteristic, device_type: str, key: str):  # pylint: disable=too-many-arguments
        Descriptor.__init__(self, bus, index, uuid, ['read'], characteristic)
        self.device_type = device_type
        self.key = key
        self.value = dbus_util.str_to_byte_array(
            self.read_network_device_active_connection_setting())

    def read_network_device_active_connection_setting(self):
        """
        Read network device active connection setting
        """
        device = nm_util.get_current_device(self.device_type)
        if device is not None:
            active_conn = device.ActiveConnection
            if active_conn is not None:
                conn_sets = active_conn.Connection.GetSettings()
                if conn_sets is not None:
                    return deep_get(conn_sets, self.key, "")
        return ""

    def ReadValue(self, _options):
        """
        Read value
        """
        set_value = self.read_network_device_active_connection_setting()
        self.value = dbus_util.str_to_byte_array(set_value)
        logger.info(
            f"read NM {self.device_type} device active connection setting {self.key}={set_value}")
        return self.value


class NetworkManagerStateCharacteristic(Characteristic):
    """
    Service for network manager state
    Expose wireless enabled, networking enabled, connectivity state and network manager state
    """
    NETWORK_MANAGER_STATE_CHRC_UUID = '22345678-1234-5678-1234-56781abcdee2'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.NETWORK_MANAGER_STATE_CHRC_UUID,
            ['read', 'notify'],
            service)

        # initialize value
        self.notifying = False
        logger.info(
            f'initialize NM state characteristic: {self.NETWORK_MANAGER_STATE_CHRC_UUID}')
        self.value = self.read_network_manager_state()
        GObject.timeout_add(5000, self.notify_network_manager_state)

    def read_network_manager_state(self):
        """
        Read network manager state
        """
        wireless_enabled = NetworkManager.WirelessEnabled
        networking_enabled = NetworkManager.NetworkingEnabled
        connectivity = NetworkManager.Connectivity
        state = NetworkManager.State
        logger.info(
            f"""NM state: wireless enabled: {wireless_enabled}, networking enabled: {networking_enabled}, connectivity state: {const('connectivity', connectivity)}, state: {const('state', state)}""")  # pylint: disable=line-too-long
        return [wireless_enabled, networking_enabled, connectivity, state]

    def notify_network_manager_state(self):
        """
        Notify network manager state
        """
        if self.notifying:
            new_value = self.read_network_manager_state()
            logger.debug(f'notify NM state {repr(new_value)}')
            self.value = new_value
            # TODO: Find a better way
            self.PropertiesChanged(
                GATT_CHRC_IFACE, {'Value': [
                    dbus.Byte(new_value[0]),
                    dbus.Byte(new_value[1]),
                    dbus.Byte(new_value[2]),
                    dbus.Byte(new_value[3])]}, [])
        return True

    def ReadValue(self, _options):
        """
        Read value
        """
        self.value = self.read_network_manager_state()
        logger.info(f"read NM state: {repr(self.value)}")
        return self.value

    def StartNotify(self):
        """
        Start notifying
        """
        logger.info('start notifying NM state')
        if not self.notifying:
            self.notifying = True
            self.notify_network_manager_state()

    def StopNotify(self):
        """
        Stop notifying
        """
        logger.info('stop notifying NM state')
        if self.notifying:
            self.notifying = False


class NetworkWirelessConfigurationCharacteristic(Characteristic):
    """
    Configure wireless network
    """
    CHRC_UUID = '97345678-1234-5678-1234-56781abddee2'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.CHRC_UUID,
            ['secure-write'],
            service)

        self.value = []
        logger.info(
            f'initialize NM network configuration characteristic: {self.CHRC_UUID}')

    def WriteValue(self, value, _options):
        """
        Write value
        """
        logger.info('write value to network wireless configuration')
        try:
            parsed_values = urllib.parse.parse_qs(
                ''.join([str(v) for v in value]))

            # TODO: Better extraction of values
            ssid = deep_get(parsed_values, 'ssid', None)
            if ssid is not None:
                if len(ssid) >= 1:
                    ssid = ssid[0]

            psk = deep_get(parsed_values, 'psk', None)
            if psk is not None:
                if len(psk) >= 1:
                    psk = psk[0]

            # TODO: Better handling of wireless connections instead of nuking them
            wireless_connections = nm_util.get_all_wireless_connections()
            for conn in wireless_connections:
                conn_uuid = conn.GetSettings()['connection']['uuid']
                nm_util.delete_network_connection_by_uuid(conn_uuid)

            # TODO: Better handling of networking configuration
            if ssid != "" and psk != "":
                nm_util.add_wireless_connection(ssid, psk)

        except TypeError as exc:
            raise InvalidArgsException() from exc
