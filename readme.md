# WIFIBT-CONNECT

An experimental utility for configuring WIFI network using Bluetooth BLE.

## Service

This utility expose a service :

```
UUID = 22345678-1234-5678-1234-56789abcdef1
```

**Values**

| Bytes | Description                                                                                                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | [Wireless enabled](https://developer-old.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html#gdbus-property-org-freedesktop-NetworkManager.WirelessEnabled)     |
| 1     | [Networking enabled](https://developer-old.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html#gdbus-property-org-freedesktop-NetworkManager.NetworkingEnabled) |
| 2     | [Connectivity state](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMConnectivityState)                                                                    |
| 3     | [Network manager state](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMState)                                                                             |

## Characteristics

This service is composed of many characteristics :

### Network Manager Status

```
UUID = 22345678-1234-5678-1234-56781abcdee2
```

Implements `read` and `notify` flags

### Ethernet & WIFI device state

There is one characteristic for each device type.

```
Ethernet UUID = 32345678-1234-5678-1234-56781abcdee2
WIFI UUID = 42345678-1234-5678-1234-56781abcdee2
```

Implements `read` and `notify` flags

**Values**

| Bytes | Description                                                                                                         |
| ----- | ------------------------------------------------------------------------------------------------------------------- |
| 0     | [Device state](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMDeviceState)              |
| 1     | [Device state reason](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMDeviceStateReason) |

### WIFI Configuration

Characterisitc that allow for the configuration of the wireless device.

```
UUID = 97345678-1234-5678-1234-56781abddee2
```

Implements `write` flags

You can write a text with the format below to this characteristic in order to configure the wireless device.

```
ssid=router-ssid&psk=your-wifi-password
```

You can subscribe to the **Network Manager Status** and **WIFI device state** characteristics in order to be notified on changes in connectivity state.
