#include <WiFiNINA.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHT_PIN 2              
#define DHT_TYPE DHT22         
#define MQ2_PIN A0             

DHT dhtSensor(DHT_PIN, DHT_TYPE);

const char* WIFI_SSID = "12345678";           // WiFi SSID
const char* WIFI_PASSWORD = "12345678";    // WiFi password
const char* MQTT_BROKER = "broker.hivemq.com"; // MQTT broker
const char* MQTT_TOPIC = "Home/SensorData"; // MQTT topic for sensor data

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void connectToWiFi() {
  Serial.print("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void connectToMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqttClient.connect("NanoClient")) { // Unique client ID
      Serial.println("Connected to MQTT broker!");
    } else {
      Serial.print("Failed. Error code: ");
      Serial.println(mqttClient.state());
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  dhtSensor.begin();

  connectToWiFi();
  
  mqttClient.setServer(MQTT_BROKER, 1883);
  connectToMQTT();
}

void loop() {
  mqttClient.loop();

  // Reading temperature and humidity from DHT22 sensor
  float temp = dhtSensor.readTemperature();
  float hum = dhtSensor.readHumidity();

  // Reading smoke level from MQ2 sensor
  int mq2Reading = analogRead(MQ2_PIN);
  float smokeLevel = map(mq2Reading, 0, 1023, 0, 100); // Scale to percentage

  // Check for valid readings
  if (isnan(temp) || isnan(hum)) {
    Serial.println("Error reading DHT sensor data!");
    return;
  }

  // Construct the sensor data message
  String payload = String("{\"Temperature\":") + temp +
                   ",\"Humidity\":" + hum +
                   ",\"SmokeLevel\":" + smokeLevel + "}";

  // Publish to the MQTT topic
  if (mqttClient.publish(MQTT_TOPIC, payload.c_str())) {
    Serial.println("Published data successfully:");
    Serial.println(payload);
  } else {
    Serial.println("Failed to publish data.");
  }

  delay(5000); // Wait before taking the next reading
}
