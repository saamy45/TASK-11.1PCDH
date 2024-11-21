import os
import requests
from paho.mqtt import client as mqtt_client

# Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "Home/SensorData"

FIREBASE_SECRET = os.getenv("FIREBASE_SECRET")
FIREBASE_URL = "https://embedded-1system-default-rtdb.firebaseio.com"

# Validate Firebase secret
if not FIREBASE_SECRET:
    raise EnvironmentError("FIREBASE_SECRET is not set. Please set the environment variable and try again.")

# Function to send sensor data to Firebase
def send_data_to_firebase(data):
    formatted_data = {"SensorData": data}
    firebase_endpoint = f"{FIREBASE_URL}/SensorData.json?auth={FIREBASE_SECRET}"
    try:
        response = requests.patch(firebase_endpoint, json=formatted_data)
        if response.ok:
            print(f"Successfully updated Firebase with data: {data}")
        else:
            print(f"Failed to update Firebase. Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred while updating Firebase: {e}")

# MQTT Callbacks
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with return code {rc}")

def handle_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        print(f"Message received from topic {message.topic}: {payload}")
        send_data_to_firebase(payload)
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# Initialize and run the MQTT client
def run_mqtt_client():
    mqtt_client_instance = mqtt_client.Client()
    mqtt_client_instance.on_connect = handle_connect
    mqtt_client_instance.on_message = handle_message

    try:
        mqtt_client_instance.connect(MQTT_BROKER, MQTT_PORT)
        mqtt_client_instance.loop_forever()
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

if __name__ == "__main__":
    run_mqtt_client()
