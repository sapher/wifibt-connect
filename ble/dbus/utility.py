import dbus


def str_to_byte_array(string: str) -> bytearray:
    """
    Convert string to DBus byte array
    """
    byte_array = []
    for c in string:
        byte_array.append(dbus.Byte(ord(c)))
    return byte_array
