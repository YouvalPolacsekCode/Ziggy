import paho.mqtt.client as mqtt

# Device control logic for Zigbee, IR, etc., now with MQTT capabilities

class MqttDeviceController:
    def __init__(self, broker_address, broker_port=1883, username=None, password=None, devices_config=None):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.devices_config = devices_config or {} # Store device mapping
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self):
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(self.broker_address, self.broker_port, 60)
            self.client.loop_start()  # Start the MQTT client loop in a non-blocking way
            print(f"[MQTT] Connecting to broker at {self.broker_address}:{self.broker_port}")
        except Exception as e:
            print(f"[MQTT ERROR] Failed to connect to broker: {e}")

    def disconnect(self):
        self.client.loop_stop() # Stop the MQTT client loop
        self.client.disconnect()
        print("[MQTT] Disconnected from broker")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connected successfully")
            # Subscribe to state topics if defined in devices config
            self._subscribe_to_state_topics()
        else:
            print(f"[MQTT ERROR] Connection failed with code {rc}")

    def _subscribe_to_state_topics(self):
        for device_name, device_info in self.devices_config.items():
            state_topic = device_info.get("state_topic")
            if state_topic:
                self.client.subscribe(state_topic)
                print(f"[MQTT] Subscribed to state topic: {state_topic}")

    def _on_message(self, client, userdata, msg):
        print(f"[MQTT] Received message on topic {msg.topic}: {msg.payload.decode()}")
        # Process incoming messages (e.g., device state updates)
        # You can update internal device states or trigger actions here

    def publish(self, topic, payload, qos=0, retain=False):
        try:
            self.client.publish(topic, payload, qos, retain)
            print(f"[MQTT] Published message to topic {topic}")
        except Exception as e:
            print(f"[MQTT ERROR] Failed to publish message: {e}")

    def control_device(self, device_name, action, value=None):
        """Controls a device via MQTT based on device name and action."""
        device_info = self.devices_config.get(device_name.lower())

        if not device_info:
            print(f"[MQTT ERROR] Device '{device_name}' not found in configuration.")
            return

        command_topic = device_info.get("command_topic")
        if not command_topic:
            print(f"[MQTT ERROR] Command topic not defined for device '{device_name}'.")
            return

        # Determine payload based on action and device component
        payload = None
        component = device_info.get("component")

        if component == "light":
            if action in ["on", "off", "toggle"]:
                payload = action.upper()
            # Add handling for brightness, color, etc. here if needed
            # elif action == "set_brightness" and value is not None:
            #     payload = json.dumps({"brightness": value})

        elif component == "climate":
            if action == "set_temperature" and value is not None:
                payload = str(value) # Temperature usually sent as a string
            # Add handling for HVAC mode, fan mode, etc.

        # Add handling for other components (switch, cover, etc.)

        if payload is not None:
            self.publish(command_topic, payload)
            print(f"[MQTT] Sent '{payload}' command to '{device_name}'.")
        else:
            print(f"[MQTT ERROR] Unsupported action '{action}' for device '{device_name}'.")


# Example usage (will be integrated into ziggy_main.py)
# if __name__ == "__main__":
#     controller = MqttDeviceController("your_mqtt_broker_address")
#     controller.connect()
#     # Keep the script running to maintain connection
#     import time
#     try:
#         while True:
#             time.sleep(1);
#     except KeyboardInterrupt:
#         controller.disconnect()
