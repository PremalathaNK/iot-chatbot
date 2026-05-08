

#include <WiFi.h>
#include <WebServer.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = "vivoT2x5G";
const char* password = "prema123";

WebServer server(80);

#define LED_PIN       2
#define BUZZER_PIN    14
#define RELAY_PIN     13
#define RGB_PIN       4
#define DHT_PIN       32
#define LDR_PIN       36

#define DHTTYPE DHT11

DHT dht(DHT_PIN, DHTTYPE);

Adafruit_NeoPixel rgb(1, RGB_PIN, NEO_GRB + NEO_KHZ800);

bool smartMode = false;

void setRGB(int r, int g, int b) {
  rgb.setPixelColor(0, rgb.Color(r, g, b));
  rgb.show();
}

void melody() {
  tone(BUZZER_PIN, 262);
  delay(200);

  tone(BUZZER_PIN, 330);
  delay(200);

  tone(BUZZER_PIN, 392);
  delay(200);

  noTone(BUZZER_PIN);
}

void setup() {

  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);

  rgb.begin();
  rgb.show();

  dht.begin();

  WiFi.begin(ssid, password);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected");
  Serial.println(WiFi.localIP());

  // LIGHT ON
  server.on("/lighton", []() {
    digitalWrite(LED_PIN, HIGH);
    server.send(200, "text/plain", "LIGHT ON");
  });

  // LIGHT OFF
  server.on("/lightoff", []() {
    digitalWrite(LED_PIN, LOW);
    server.send(200, "text/plain", "LIGHT OFF");
  });

  // RGB RED
  server.on("/rgbred", []() {
    setRGB(255, 0, 0);
    server.send(200, "text/plain", "RGB RED");
  });

  // RGB BLUE
  server.on("/rgbblue", []() {
    setRGB(0, 0, 255);
    server.send(200, "text/plain", "RGB BLUE");
  });

  // RGB OFF
  server.on("/rgboff", []() {
    setRGB(0, 0, 0);
    server.send(200, "text/plain", "RGB OFF");
  });

  // RELAY ON
  server.on("/relayon", []() {
    digitalWrite(RELAY_PIN, HIGH);
    server.send(200, "text/plain", "RELAY ON");
  });

  // RELAY OFF
  server.on("/relayoff", []() {
    digitalWrite(RELAY_PIN, LOW);
    server.send(200, "text/plain", "RELAY OFF");
  });

  // BUZZER ON
  server.on("/buzzeron", []() {
    tone(BUZZER_PIN, 1000);
    server.send(200, "text/plain", "BUZZER ON");
  });

  // BUZZER OFF
  server.on("/buzzeroff", []() {
    noTone(BUZZER_PIN);
    server.send(200, "text/plain", "BUZZER OFF");
  });

  // MELODY
  server.on("/melody", []() {
    melody();
    server.send(200, "text/plain", "MELODY");
  });

  // TEMPERATURE
  server.on("/temperature", []() {

    float t = dht.readTemperature();

    if (isnan(t)) {
      server.send(200, "text/plain", "ERROR");
      return;
    }

    server.send(200, "text/plain", String(t));
  });

  // LDR
  server.on("/ldr", []() {

    int value = analogRead(LDR_PIN);

    server.send(200, "text/plain", String(value));
  });

  // SMART MODE
  server.on("/smartmode", []() {
    smartMode = true;
    server.send(200, "text/plain", "SMART MODE");
  });

  server.begin();

  Serial.println("Server Started");
}

void loop() {

  server.handleClient();

  // SMART STREET LIGHT
  if (smartMode) {

    int ldr = analogRead(LDR_PIN);

    Serial.println(ldr);

    if (ldr < 1500) {
      setRGB(255, 255, 255);
    }
    else {
      setRGB(0, 0, 0);
    }
  }
}