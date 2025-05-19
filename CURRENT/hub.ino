#include <WiFi.h>
#include <esp_now.h>

const int MOTOR_PIN_5 = 5;
const int MOTOR_PIN_19 = 19;
const int MOTOR_PIN_21 = 21;
const int MOTOR_PIN_4 = 4;

// Wi-Fi AP credentials
#define WIFI_SSID "ESP32_AP"
#define WIFI_PASS "12345678"  // Must be at least 8 characters
#define AP_CHANNEL 1          // Explicitly set the AP channel

// TCP server port
#define TCP_PORT 80

WiFiServer tcpServer(TCP_PORT);

// Broadcast MAC address for ESP-NOW (to send to all peers)
uint8_t broadcastAddress[] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("ESP-NOW broadcast status: ");
  Serial.println((status == ESP_NOW_SEND_SUCCESS) ? "Success" : "Failure");
}

void setup() {
  Serial.begin(115200);
  Serial.println("ESP32 ESP-NOW Relay Starting...");

  pinMode(MOTOR_PIN_5, OUTPUT);
  pinMode(MOTOR_PIN_19, OUTPUT);
  pinMode(MOTOR_PIN_21, OUTPUT);
  pinMode(MOTOR_PIN_4, OUTPUT);

  // Set Wi-Fi mode to AP+STA for proper ESP-NOW operation with a soft AP.
  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(WIFI_SSID, WIFI_PASS, AP_CHANNEL);
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());

  tcpServer.begin();
  Serial.println("TCP server started on port " + String(TCP_PORT));

  // Initialize ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  Serial.println("ESP-NOW initialized.");

  // Register the send callback
  esp_now_register_send_cb(OnDataSent);

  // Configure the broadcast peer
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = AP_CHANNEL;  // Use the same channel as the AP
  peerInfo.encrypt = false;

  // Add the broadcast peer
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add ESP-NOW broadcast peer");
    return;
  }
  Serial.println("Broadcast peer added successfully.");
}

void loop() {
  WiFiClient client = tcpServer.available();
  if (client) {
    Serial.println("Client connected.");

    unsigned long startTime = millis();
    while (!client.available() && millis() - startTime < 5000) {
      delay(10);
    }

    if (client.available()) {
      String received = client.readStringUntil('\n');
      received.trim();
      Serial.print("Received: ");
      Serial.println(received);

      int len = received.length() + 1;
      char message[len];
      received.toCharArray(message, len);

      esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)message, len);
      if (result == ESP_OK) {
        Serial.println("Message broadcasted successfully via ESP-NOW");
      } else {
        Serial.print("Error broadcasting message via ESP-NOW: ");
        Serial.println(result);
      }

      client.println("Message relayed via ESP-NOW.");

      // Find ';' which separates the row
      int separator1 = received.indexOf(';');
      if (separator1 == -1) {
        Serial.println("Invalid command format (missing semicolon).");
        return;
      }

      // Find ':' which separates the pin number from the command
      int separator2 = received.indexOf(':');
      if (separator2 == -1) {
        Serial.println("Invalid command format (missing colon).");
        return;
      }

      // Extract the row part and the command part
      String row = received.substring(0, separator1);
      row.trim();
      if (row != "0") {
        return;
      }

      String pinStr = received.substring(separator1 + 1, separator2);
      String cmd = received.substring(separator2 + 1);

      // Trim whitespace from the command (removes leading/trailing whitespace)
      cmd.trim();

      // Convert the pin substring to an integer
      int pin = pinStr.toInt();

      // Validate that the pin is one of our motor pins
      if (pin != MOTOR_PIN_5 && pin != MOTOR_PIN_19 && pin != MOTOR_PIN_21 && pin != MOTOR_PIN_4) {
        Serial.println("Invalid motor pin.");
        return;
      }

      Serial.printf("  Pin parsed: %d\n", pin);
      Serial.printf("  Command parsed: \"%s\"\n", cmd.c_str());

      // Execute the command: "1" to turn the motor ON, "0" to turn it OFF
      if (cmd == "1") {
        digitalWrite(pin, HIGH);
        Serial.printf("Motor ON at pin %d\n", pin);
      } else if (cmd == "0") {
        digitalWrite(pin, LOW);
        Serial.printf("Motor OFF at pin %d\n", pin);
      } else {
        Serial.println("Invalid command received.");
      }
    } else {
      Serial.println("No data received from client within timeout.");
    }
  }
  delay(10);
}
