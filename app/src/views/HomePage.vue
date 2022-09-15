<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar>
        <ion-title>BLE debug</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <ion-button :disabled="!scanButtonEnabled" @:click="scanForDevices()">
        <ion-icon expand="full" :icon="bluetooth"></ion-icon>
        <ion-text>Scan for devices</ion-text>
      </ion-button>

      <ion-list>
        <ion-item
          @click="connectToDevice(device.id)"
          v-for="device in devices.value"
          :key="device.id"
        >
          <ion-icon
            v-if="device.state == 'connected'"
            slot="start"
            :icon="radioButtonOn"
            color="primary"
          ></ion-icon>
          <ion-icon v-else slot="start" :icon="radioButtonOff"></ion-icon>
          {{ device.name }}
        </ion-item>
      </ion-list>

      <ion-card v-if="currentDeviceId">
        <ion-item>
          <ion-text>Device name</ion-text>
          <ion-text slot="end">{{ currentDevice?.name }}</ion-text>
        </ion-item>
        <ion-item>
          <ion-text>Connectivity state</ion-text>
          <ion-text slot="end">{{
            currentDeviceNetworkingState?.connectivityState
          }}</ion-text>
        </ion-item>
        <ion-item>
          <ion-text>Wireless enabled</ion-text>
          <ion-text slot="end">{{
            currentDeviceNetworkingState?.wirelessEnabled
          }}</ion-text>
        </ion-item>
        <!-- Configure network modal -->
        <ion-button id="open-modal">Configure wifi</ion-button>
        <ion-modal trigger="open-modal">
          <ion-header>
            <ion-toolbar>
              <ion-buttons>
                <ion-button>Cancel</ion-button>
              </ion-buttons>
              <ion-title>Network configuration</ion-title>
            </ion-toolbar>
          </ion-header>
          <ion-content>
            <ion-list>
              <ion-item>
                <ion-label>SSID</ion-label>
                <ion-input></ion-input>
              </ion-item>
              <ion-item>
                <ion-label>Password</ion-label>
                <ion-input></ion-input>
              </ion-item>
              <ion-item>
                <ion-button @click="configureWifiNetwork()" expand="block"
                  >Configure</ion-button
                >
              </ion-item>
            </ion-list>
          </ion-content>
        </ion-modal>
      </ion-card>
    </ion-content>
  </ion-page>
</template>

<script lang="ts" setup>
import { bluetooth, radioButtonOff, radioButtonOn } from "ionicons/icons";
import { reactive, ref } from "vue";
import {
  IonContent,
  IonHeader,
  IonModal,
  IonButtons,
  IonLabel,
  IonInput,
  IonPage,
  IonCard,
  IonText,
  IonTitle,
  IonToolbar,
  IonButton,
  IonIcon,
  IonList,
  IonItem,
} from "@ionic/vue";
import { BLE } from "@awesome-cordova-plugins/ble";
import { filter } from "rxjs";
import { computed } from "@vue/reactivity";

// constants
const NETWORK_SERVICE_UUID = "02345678-1234-5678-1234-56789abcdef1";
const CONNECTIVITY_STATE_CHRC_UUID = "12345678-1234-5678-1234-56781abcdee2";
const NETWORK_CONFIGURATION_CHRC_UUID = "92345678-1234-5678-1234-56781abddee2";

type DeviceId = string;

interface NetworkingState {
  wirelessEnabled: boolean | undefined;
  connectivityState: string | undefined;
}

interface Characteristic {
  characteristic: string;
  service: string;
  isNotifying: boolean;
  properties: Array<string>;
}

interface Device {
  id: DeviceId;
  name: string;
  state: string;
  services: Array<string>;
  characteristics: Characteristic[];
}

const networkingState = reactive<Record<DeviceId, NetworkingState>>({});
const scanButtonEnabled = ref(true);
const devices = reactive<{ value: Array<Device> }>({ value: [] });
const currentDeviceId = ref("");
const currentDevice = computed(() =>
  devices.value.find((d) => d.id === currentDeviceId.value)
);
const currentDeviceNetworkingState = computed(
  () => networkingState[currentDeviceId.value]
);

/**
 * Convert buffer to string
 * @param buffer
 */
function convertBufferToString(buffer): string {
  return String.fromCharCode.apply(null, new Uint8Array(buffer));
}

/**
 * Scan for devices
 */
async function scanForDevices() {
  // scanButtonEnabled.value = false
  devices.value = [];

  BLE.scan([], 10)
    .pipe(filter((device) => device.name === "gardenator"))
    .subscribe(
      (device: Device) => {
        devices.value.push(device);
      },
      (err) => {
        scanButtonEnabled.value = true;
      },
      () => {
        scanButtonEnabled.value = true;
      }
    );
}

/**
 * Connect to device
 * @param deviceId
 */
async function connectToDevice(deviceId: string) {
  console.log(`connect to device: ${deviceId}`);

  BLE.connect(deviceId).subscribe((device: Device) => {
    console.log(`effectively connected to device ${deviceId}`);

    // Check if contain required service
    /* if (!device.services.includes(NETWORK_SERVICE_UUID)) {
        console.error(`device ${deviceId} doesn't have required service`)
        return;
      } */

    const index = devices.value.findIndex((d) => d.id === device.id);
    devices.value[index] = device;
    currentDeviceId.value = device.id;

    BLE.startNotification(
      deviceId,
      NETWORK_SERVICE_UUID,
      CONNECTIVITY_STATE_CHRC_UUID
    ).subscribe((buffer) => {
      networkingState[deviceId] = {
        connectivityState: convertBufferToString(buffer[0]),
        wirelessEnabled: false,
      };
    });
  }, console.error);
}

async function configureWifiNetwork() {
  console.log(`configure wifi network`);
}
</script>

<style scoped></style>
