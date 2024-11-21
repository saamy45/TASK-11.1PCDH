import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import tkinter as tk
import threading

# MQTT broker and topic details
broker = "broker.hivemq.com"
topic = "Home/SensorData"

# GPIO setup
alert_pin = 17  # Change this to the GPIO pin you want to use
GPIO.setmode(GPIO.BCM)
GPIO.setup(alert_pin, GPIO.OUT)
GPIO.output(alert_pin, GPIO.LOW)  # Set pin to LOW initially

# Temperature threshold
TEMP_THRESHOLD = 30.0  # Adjust this to your desired threshold

# GUI setup
root = tk.Tk()
root.title("Temperature and Smoke Alert")
root.geometry("400x300")  # Set a bigger window size

# Create labels to display sensor values
temperature_label = tk.Label(root, text="Temperature: -- °C", font=("Helvetica", 16))
temperature_label.pack()

humidity_label = tk.Label(root, text="Humidity: -- %", font=("Helvetica", 16))
humidity_label.pack()

smoke_level_label = tk.Label(root, text="Smoke Level: -- %", font=("Helvetica", 16))
smoke_level_label.pack()

# Add a label for alert status
alert_label = tk.Label(root, text="Alert: --", font=("Helvetica", 16))
alert_label.pack()

def on_message(client, userdata, msg):
    data = msg.payload.decode()
    print(f"Received sensor data: {data}")  # Print the raw data for debugging

    try:
        # Look for key-value pairs in the data, e.g., "Temperature: 25.5, Humidity: 60, SmokeLevel: 10"
        # Ensure the string is split correctly
        parts = data.split(',')
        
        # Extract each value (Temperature, Humidity, SmokeLevel)
        temperature_str = next((item for item in parts if "Temperature" in item), "").split(":")[1].strip()
        humidity_str = next((item for item in parts if "Humidity" in item), "").split(":")[1].strip()
        smoke_level_str = next((item for item in parts if "SmokeLevel" in item), "").split(":")[1].strip()
        
        # Convert them to float
        temperature = float(temperature_str)
        humidity = float(humidity_str)
        smoke_level = float(smoke_level_str)

        print(f"Extracted Temperature: {temperature} °C")
        print(f"Extracted Humidity: {humidity} %")
        print(f"Extracted Smoke Level: {smoke_level} %")
        
        # Update GUI with received values
        temperature_label.config(text=f"Temperature: {temperature} °C")
        humidity_label.config(text=f"Humidity: {humidity} %")
        smoke_level_label.config(text=f"Smoke Level: {smoke_level} %")
        
        # Check if temperature exceeds the threshold and update the GPIO pin
        if temperature > TEMP_THRESHOLD:
            GPIO.output(alert_pin, GPIO.HIGH)
            alert_label.config(text="Alert: Temperature threshold exceeded!", fg="red")
            print("Temperature threshold exceeded! GPIO pin set to HIGH.")
        else:
            GPIO.output(alert_pin, GPIO.LOW)
            alert_label.config(text="Alert: Temperature is normal.", fg="green")
            print("Temperature below threshold. GPIO pin set to LOW.")
            
    except (ValueError, IndexError) as e:
        print(f"Error parsing sensor data: {e}")
        alert_label.config(text="Error parsing data!", fg="orange")

# Initialize MQTT client
client = mqtt.Client()
client.connect(broker, 1883)

# Assign callback function
client.on_message = on_message

# Subscribe to the topic
client.subscribe(topic)

# Start listening for incoming messages
print("Listening for sensor data...")

# Run MQTT client loop in a separate thread to avoid blocking the main thread
def run_mqtt():
    client.loop_forever()

mqtt_thread = threading.Thread(target=run_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# Run the GUI
root.mainloop()
