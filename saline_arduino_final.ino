#include <HX711.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Servo.h>

// ---- WIFI CONFIG ----
const char* ssid     = "Iqoo123";
const char* password = "12345678";
const char* serverURL = "http://192.168.1.9:5000/update";

// ---- PIN CONFIG ----
#define DOUT_PIN 14   // DT  -> GPIO14
#define SCK_PIN  13   // SCK -> GPIO13
#define SERVO_PIN 12   // GPIO12
#define BUZZER_PIN 4   // GPIO4

HX711 scale;
Servo alertServo;

// Keep the calibration value that matches YOUR sensor.
// This is separate from the 160g full-scale reference.
float calibrationFactor = -75.0;

// Fixed max saline weight for percentage calculation.
const float fullBagWeight = 160.0;

bool alertActive = false;

float readAverageWeight(uint8_t samples = 10) {
  float total = 0.0;
  for (uint8_t i = 0; i < samples; i++) {
    total += scale.get_units(1);
    delay(5);
  }
  return total / samples;
}

void setup() {
  Serial.begin(115200);

  // HX711 setup
  scale.begin(DOUT_PIN, SCK_PIN);
  scale.set_scale(calibrationFactor);
  scale.tare(20);
  delay(1500);
  scale.tare(20);

  // Servo setup
  alertServo.attach(SERVO_PIN);
  alertServo.write(0);

  // Buzzer setup
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // WiFi connect
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.println("ESP IP: " + WiFi.localIP().toString());
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    delay(1000);
    return;
  }

  if (!scale.is_ready()) {
    Serial.println("HX711 not ready");
    delay(1000);
    return;
  }

  float currentWeight = readAverageWeight(10);

  if (currentWeight < 5.0) currentWeight = 0.0;

  float percentage = (currentWeight / fullBagWeight) * 100.0;
  percentage = constrain(percentage, 0, 100);

  Serial.println("Weight: " + String(currentWeight, 2) + " | " + String(percentage, 1) + "%");

  if (percentage < 30.0 && !alertActive) {
    alertActive = true;
    alertServo.write(90);
    digitalWrite(BUZZER_PIN, HIGH);
  } else if (percentage >= 30.0 && alertActive) {
    alertActive = false;
    alertServo.write(0);
    digitalWrite(BUZZER_PIN, LOW);
  }

  WiFiClient client;
  HTTPClient http;
  http.begin(client, serverURL);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  String postData = "weight=" + String(currentWeight, 2) +
                    "&percentage=" + String(percentage, 1) +
                    "&alert=" + String(alertActive ? "1" : "0");

  int httpCode = http.POST(postData);
  Serial.println("HTTP: " + String(httpCode));
  http.end();

  delay(2000);
}
