from uuid import uuid4
import logging
from NetworkManager import NetworkManager, const, Settings

logger = logging.getLogger('wfbt')


def get_devices():
    """
    Get all network devices
    """
    return NetworkManager.GetAllDevices()


def get_devices_by_type(device_type: str):
    """
    Get devices by type
    """
    return list(filter(lambda _device: const('device_type', _device.DeviceType) in [device_type], get_devices()))


def get_current_device(device_type: str):
    """
    Get current device by type
    """
    devices = get_devices_by_type(device_type)
    return None if len(devices) <= 0 else devices[0]


def get_all_wireless_connections():
    """
    Get all wireless connections
    """
    wireless_connections = []
    connections = Settings.ListConnections()
    # filter connections
    for conn in connections:
        settings = conn.GetSettings()
        settings_conn = settings['connection']
        if "type" in settings_conn:
            if settings_conn['type'] == "802-11-wireless":
                wireless_connections.append(conn)
    return wireless_connections


def delete_network_connection_by_uuid(uuid: str):
    """
    Delete network connection by UUID
    """
    connection = Settings.GetConnectionByUuid(uuid)
    return connection.Delete()


def add_wireless_connection(ssid: str, password: str):
    """
    Add wireless connection
    """
    conn = {
        '802-11-wireless': {
            'ssid': ssid,
        },
        '802-11-wireless-security': {
            "key-mgmt": "wpa-psk",
            "auth-alg": "open",
            "psk": password
        },
        'connection': {
            'id': ssid,
            'type': '802-11-wireless',
            'uuid': str(uuid4())
        },
        'ipv4': {'method': 'auto'},
        'ipv6': {'method': 'auto'}
    }
    return Settings.AddConnection(conn)
