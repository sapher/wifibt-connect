# WIFIBT-CONNECT

An experimental utility for configuring WIFI network using Bluetooth LE.

It offer ways to monitor connectivity state, `wifi` and `ethernet` device state and ways to configure wifi network.

It only support raspberry pi3 and pi4 running Linux.

The distribution needs to have `network-manager` installed.

## Configuration

**Install dependencies**

```shell
apt-get install libbluetooth-dev python-dev libglib2.0-dev libboost-python-dev libboost-thread-dev -y
```

**Configure network manager**

```shell
sudo systemctl stop networking
sudo systemctl disable networking
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

**Install virtualenv dependencies**

```shell
virtualenv venv
source venv/bin/activate
pip3 install
PYGOBJECT_WITHOUT_PYCAIRO=1 pip3 install --no-build-isolation pygobject
```

**Configure BLE device**

```shell
hciconfig hci0 piscan
hciconfig hci0 sspmode 1
hciconfig hci0 up
```

**Run docker image**

```shell
docker build -t wifibt .
sudo docker run -it --rm --network host --cap-add=NET_ADMIN --privileged=true --volume /var/run/dbus:/var/run/dbus wifibt
```

## Specifications

### Service

This utility expose a service :

```
UUID = 22345678-1234-5678-1234-56789abcdef1
```

### Characteristics

This service is composed of many characteristics :

#### Network Manager Status

Expose information on the current state of the network manager.

```
UUID = 22345678-1234-5678-1234-56781abcdee2
```

Implements `read` and `notify` flags

**Values**

| Bytes | Description                                                                                                                                                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0     | [Wireless enabled](https://developer-old.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html#gdbus-property-org-freedesktop-NetworkManager.WirelessEnabled)     |
| 1     | [Networking enabled](https://developer-old.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.html#gdbus-property-org-freedesktop-NetworkManager.NetworkingEnabled) |
| 2     | [Connectivity state](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMConnectivityState)                                                                    |
| 3     | [Network manager state](https://developer-old.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMState)                                                                             |

#### Ethernet & WIFI device state

There is one characteristic for each device type, `wifi` & `ethernet`.

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

#### WIFI Configuration

Characterisitc that allow for the configuration of the wireless device.

```
UUID = 97345678-1234-5678-1234-56781abddee2
```

Implements `write` flags

You can write a text with the format below to this characteristic in order to configure the wireless device.

```
ssid=router-ssid&psk=your-wifi-password
```

You can subscribe to the **Network Manager Status** and **WIFI device state** characteristics in order to be notified of the changes in connectivity state.
