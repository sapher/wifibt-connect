import array
import logging
import dbus
from . import exceptions
from .gatt_server import Service, Characteristic, Descriptor

logger = logging.getLogger('wfbt')


class TestService(Service):
    """
    Dummy test service that provides characteristics and descriptors that
    exercise various API functionality.

    """
    TEST_SVC_UUID = '12345678-1234-5678-1234-56789abcdef0'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.TEST_SVC_UUID, True)
        self.add_characteristic(TestCharacteristic(bus, 0, self))
        self.add_characteristic(TestEncryptCharacteristic(bus, 1, self))
        self.add_characteristic(TestSecureCharacteristic(bus, 2, self))


class TestCharacteristic(Characteristic):
    """
    Dummy test characteristic. Allows writing arbitrary bytes to its value, and
    contains "extended properties", as well as a test descriptor.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef1'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.TEST_CHRC_UUID,
            ['read', 'write', 'writable-auxiliaries'],
            service)
        self.value = []
        self.add_descriptor(TestDescriptor(bus, 0, self))
        self.add_descriptor(
            CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, _options):
        logger.info(f"TestCharacteristic Read: {repr(self.value)}")
        return self.value

    def WriteValue(self, value, _options):
        logger.info(f"TestCharacteristic Write: {repr(value)}")
        self.value = value


class TestDescriptor(Descriptor):
    """
    Dummy test descriptor. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self, bus, index,
            self.TEST_DESC_UUID,
            ['read', 'write'],
            characteristic)

    def ReadValue(self, _options):
        return [
            dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.

    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.writable = 'writable-auxiliaries' in characteristic.flags
        self.value = array.array('B', b'This is a characteristic for testing')
        self.value = self.value.tolist()
        Descriptor.__init__(
            self, bus, index,
            self.CUD_UUID,
            ['read', 'write'],
            characteristic)

    def ReadValue(self, _options):
        return self.value

    def WriteValue(self, value, _options):
        if not self.writable:
            raise exceptions.NotPermittedException()
        self.value = value


class TestEncryptCharacteristic(Characteristic):
    """
    Dummy test characteristic requiring encryption.
    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef3'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.TEST_CHRC_UUID,
            ['encrypt-read', 'encrypt-write'],
            service)
        self.value = []
        self.add_descriptor(TestEncryptDescriptor(bus, 2, self))
        self.add_descriptor(
            CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, _options):
        logger.info(f"TestEncryptCharacteristic Read: {repr(self.value)}")
        return self.value

    def WriteValue(self, value, _options):
        logger.info(f"TestEncryptCharacteristic Write: {repr(value)}")
        self.value = value


class TestEncryptDescriptor(Descriptor):
    """
    Dummy test descriptor requiring encryption. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef4'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self, bus, index,
            self.TEST_DESC_UUID,
            ['encrypt-read', 'encrypt-write'],
            characteristic)

    def ReadValue(self, _options):
        return [dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')]


class TestSecureCharacteristic(Characteristic):
    """
    Dummy test characteristic requiring secure connection.

    """
    TEST_CHRC_UUID = '12345678-1234-5678-1234-56789abcdef5'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index,
            self.TEST_CHRC_UUID,
            ['secure-read', 'secure-write'],
            service)
        self.value = []
        self.add_descriptor(TestSecureDescriptor(bus, 2, self))
        self.add_descriptor(
            CharacteristicUserDescriptionDescriptor(bus, 3, self))

    def ReadValue(self, _options):
        logger.info(f"TestSecureCharacteristic Read: {repr(self.value)}")
        return self.value

    def WriteValue(self, value, _options):
        logger.info(f"TestSecureCharacteristic Write: {repr(value)}")
        self.value = value


class TestSecureDescriptor(Descriptor):
    """
    Dummy test descriptor requiring secure connection. Returns a static value.

    """
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef6'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
            self, bus, index,
            self.TEST_DESC_UUID,
            ['secure-read', 'secure-write'],
            characteristic)

    def ReadValue(self, _options):
        return [
            dbus.Byte('T'), dbus.Byte('e'), dbus.Byte('s'), dbus.Byte('t')
        ]
