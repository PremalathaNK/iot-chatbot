#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_NeoPixel.h>
#include <math.h>

// ======================================================
// WIFI CONFIG
// ======================================================

const char* ssid = "YOUR_WIFI";
const char* password = "PASSWORD";

// ======================================================
// WEB SERVER
// ======================================================

WebServer server(80);

// ======================================================
// SST IOT DEVELOPMENT BOARD PINS
// ======================================================

// ONBOARD LED
#define LED_PIN 2

// BUZZER
#define BUZZER_PIN 14

// RELAY
#define RELAY_PIN 13

// RGB LED
#define RGB_PIN 4

// LDR SENSOR
#define LDR_PIN 36

// THERMISTOR SENSOR
#define THERMISTOR_PIN 39

// ======================================================
// RGB CONFIG
// ======================================================

Adafruit_NeoPixel rgb(
  1,
  RGB_PIN,
  NEO_GRB + NEO_KHZ800
);

// ======================================================
// VARIABLES
// ======================================================

bool smartMode = false;

// ======================================================
// RGB FUNCTION
// ======================================================

void setRGB(int r, int g, int b) {

  rgb.setPixelColor(
    0,
    rgb.Color(r, g, b)
  );

  rgb.show();
}

// ======================================================
// THERMISTOR TEMPERATURE FUNCTION
// ======================================================

float readTemperature() {

  int adcValue = analogRead(THERMISTOR_PIN);

  Serial.print("ADC Value: ");
  Serial.println(adcValue);

  // Avoid invalid ADC values
  if (adcValue <= 0 || adcValue >= 4095) {
    return 0;
  }

  // Thermistor Constants
  const float SERIES_RESISTOR = 10000.0;
  const float NOMINAL_RESISTANCE = 10000.0;
  const float NOMINAL_TEMPERATURE = 25.0;
  const float B_COEFFICIENT = 3950.0;

  // Calculate resistance
  float resistance =
    SERIES_RESISTOR *
    ((4095.0 / adcValue) - 1.0);

  // Steinhart-Hart Equation
  float steinhart;

  steinhart = resistance / NOMINAL_RESISTANCE;

  steinhart = log(steinhart);

  steinhart /= B_COEFFICIENT;

  steinhart += 1.0 /
                (NOMINAL_TEMPERATURE + 273.15);

  steinhart = 1.0 / steinhart;

  steinhart -= 273.15;

  Serial.print("Temperature: ");
  Serial.println(steinhart);

  return steinhart;
}

// ======================================================
// MELODY FUNCTION
// ======================================================

void melody() {

  int notes[] = {
    262, 294, 330, 349,
    392, 440, 494, 523
  };

  for (int i = 0; i < 8; i++) {

    tone(BUZZER_PIN, notes[i]);

    delay(250);

    noTone(BUZZER_PIN);

    delay(50);
  }

  for (int i = 7; i >= 0; i--) {

    tone(BUZZER_PIN, notes[i]);

    delay(250);

    noTone(BUZZER_PIN);

    delay(50);
  }
}

// ======================================================
// DISCO MODE
// ======================================================

void discoMode() {

  int notes[] = {
    262, 330, 392, 523
  };

  for (int i = 0; i < 20; i++) {

    setRGB(
      random(0, 255),
      random(0, 255),
      random(0, 255)
    );

    tone(
      BUZZER_PIN,
      notes[random(0, 4)]
    );

    delay(200);
  }

  noTone(BUZZER_PIN);

  setRGB(0, 0, 0);
}

// ======================================================
// SETUP
// ======================================================

void setup() {

  Serial.begin(115200);

  // ======================================================
  // PIN MODES
  // ======================================================

  pinMode(LED_PIN, OUTPUT);

  pinMode(BUZZER_PIN, OUTPUT);

  pinMode(RELAY_PIN, OUTPUT);

  pinMode(LDR_PIN, INPUT);

  pinMode(THERMISTOR_PIN, INPUT);

  digitalWrite(LED_PIN, LOW);

  digitalWrite(RELAY_PIN, LOW);

  // ======================================================
  // RGB START
  // ======================================================

  rgb.begin();

  rgb.show();

  // ======================================================
  // WIFI CONNECT
  // ======================================================

  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();

  Serial.println("WiFi Connected");

  Serial.print("ESP32 IP Address: ");

  Serial.println(WiFi.localIP());

  // ======================================================
  // ROOT
  // ======================================================

  server.on("/", []() {

    server.send(
      200,
      "text/plain",
      "NEXUS AI ESP32 SERVER RUNNING"
    );
  });

  // ======================================================
  // LIGHT ON
  // ======================================================

  server.on("/lighton", []() {

    digitalWrite(LED_PIN, HIGH);

    server.send(
      200,
      "text/plain",
      "LIGHT ON"
    );
  });

  // ======================================================
  // LIGHT OFF
  // ======================================================

  server.on("/lightoff", []() {

    digitalWrite(LED_PIN, LOW);

    server.send(
      200,
      "text/plain",
      "LIGHT OFF"
    );
  });

  // ======================================================
  // RGB RED
  // ======================================================

  server.on("/rgbred", []() {

    setRGB(255, 0, 0);

    server.send(
      200,
      "text/plain",
      "RGB RED"
    );
  });

  // ======================================================
  // RGB BLUE
  // ======================================================

  server.on("/rgbblue", []() {

    setRGB(0, 0, 255);

    server.send(
      200,
      "text/plain",
      "RGB BLUE"
    );
  });

  // ======================================================
  // RGB GREEN
  // ======================================================

  server.on("/rgbgreen", []() {

    setRGB(0, 255, 0);

    server.send(
      200,
      "text/plain",
      "RGB GREEN"
    );
  });

  // ======================================================
  // RGB OFF
  // ======================================================

  server.on("/rgboff", []() {

    setRGB(0, 0, 0);

    server.send(
      200,
      "text/plain",
      "RGB OFF"
    );
  });

  // ======================================================
  // RELAY ON
  // ======================================================

  server.on("/relayon", []() {

    digitalWrite(RELAY_PIN, HIGH);

    server.send(
      200,
      "text/plain",
      "RELAY ON"
    );
  });

  // ======================================================
  // RELAY OFF
  // ======================================================

  server.on("/relayoff", []() {

    digitalWrite(RELAY_PIN, LOW);

    server.send(
      200,
      "text/plain",
      "RELAY OFF"
    );
  });

  // ======================================================
  // BUZZER ON
  // ======================================================

  server.on("/buzzeron", []() {

    tone(BUZZER_PIN, 1000);

    server.send(
      200,
      "text/plain",
      "BUZZER ON"
    );
  });

  // ======================================================
  // BUZZER OFF
  // ======================================================

  server.on("/buzzeroff", []() {

    noTone(BUZZER_PIN);

    server.send(
      200,
      "text/plain",
      "BUZZER OFF"
    );
  });

  // ======================================================
  // MELODY
  // ======================================================

  server.on("/melody", []() {

    melody();

    server.send(
      200,
      "text/plain",
      "MELODY PLAYED"
    );
  });

  // ======================================================
  // DISCO MODE
  // ======================================================

  server.on("/disco", []() {

    discoMode();

    server.send(
      200,
      "text/plain",
      "DISCO MODE"
    );
  });

  // ======================================================
  // TEMPERATURE
  // ======================================================

  server.on("/temperature", []() {

    float temperature = readTemperature();

    server.send(
      200,
      "text/plain",
      String(temperature, 1)
    );
  });

  // ======================================================
  // LDR
  // ======================================================

  server.on("/ldr", []() {

    int value = analogRead(LDR_PIN);

    server.send(
      200,
      "text/plain",
      String(value)
    );
  });

  // ======================================================
  // SMART MODE ON
  // ======================================================

  server.on("/smartmode", []() {

    smartMode = true;

    server.send(
      200,
      "text/plain",
      "SMART MODE ON"
    );
  });

  // ======================================================
  // SMART MODE OFF
  // ======================================================

  server.on("/smartmodeoff", []() {

    smartMode = false;

    setRGB(0, 0, 0);

    server.send(
      200,
      "text/plain",
      "SMART MODE OFF"
    );
  });

  // ======================================================
  // START SERVER
  // ======================================================

  server.begin();

  Serial.println("HTTP Server Started");
}

// ======================================================
// LOOP
// ======================================================

void loop() {

  server.handleClient();

  yield();

  // ======================================================
  // SMART STREET LIGHT
  // ======================================================

  if (smartMode) {

    int ldr = analogRead(LDR_PIN);

    Serial.print("LDR VALUE: ");

    Serial.println(ldr);

    // DARK CONDITION

    if (ldr < 1500) {

      setRGB(255, 255, 255);
    }

    // BRIGHT CONDITION

    else {

      setRGB(0, 0, 0);
    }
  }

  delay(100);
}