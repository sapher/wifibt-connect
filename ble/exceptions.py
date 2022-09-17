"""
DBus exceptions for Bluez
"""
import dbus
import dbus.exceptions


class InvalidArgsException(dbus.exceptions.DBusException):
    """
    Invalid arguments exception
    """
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
    """
    Not supported operation
    """
    _dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
    """
    Not permitted operation
    """
    _dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
    """
    Invalid value length
    """
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
    """
    General failure
    """
    _dbus_error_name = 'org.bluez.Error.Failed'
