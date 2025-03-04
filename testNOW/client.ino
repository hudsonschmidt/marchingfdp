#include "ESP32_NOW.h"
#include "WiFi.h"
#include <esp_mac.h>  // For the MAC2STR and MACSTR macros
#include <vector>
#include <string>     // For std::string
#include <cstring>    // For strnlen, etc.
#include <algorithm>  // For std::remove and std::remove_if

/* Definitions */
#define ESPNOW_WIFI_CHANNEL 6
const int MOTOR_PIN_5 = 5;
const int MOTOR_PIN_19 = 19;
const int MOTOR_PIN_21 = 21;
const int MOTOR_PIN_4 = 4;

/* Classes */
// Creating a new class that inherits from the ESP_NOW_Peer class.
class ESP_NOW_Peer_Class : public ESP_NOW_Peer {
public:
  // Constructor of the class
  ESP_NOW_Peer_Class(const uint8_t *mac_addr, uint8_t channel,
                     wifi_interface_t iface, const uint8_t *lmk)
    : ESP_NOW_Peer(mac_addr, channel, iface, lmk) {}

  // Destructor of the class
  ~ESP_NOW_Peer_Class() {}

  // Function to register the master peer
  bool add_peer() {
    if (!add()) {
      log_e("Failed to register the broadcast peer");
      return false;
    }
    return true;
  }

  // Function to handle received messages from the master
  void onReceive(const uint8_t *value, size_t len, bool broadcast) override {
    Serial.printf("Received a message from master " MACSTR " (%s)\n",
                  MAC2STR(addr()), (broadcast ? "broadcast" : "unicast"));

    // Safely find the actual length up to the first null byte, to avoid trailing zeros:
    size_t actualLen = strnlen((const char *)value, len);

    // Convert raw bytes to a std::string up to that length
    std::string rx_message((const char *)value, actualLen);

    // Remove possible carriage-return or newline from the string
    rx_message.erase(std::remove(rx_message.begin(), rx_message.end(), '\r'), rx_message.end());
    rx_message.erase(std::remove(rx_message.begin(), rx_message.end(), '\n'), rx_message.end());

    Serial.printf("  Raw Message: \"%s\"\n", rx_message.c_str());

    if (rx_message.empty()) {
      // If the message is empty, do nothing
      return;
    }

    // Find ':' which separates the pin number from the command
    size_t separator = rx_message.find(':');
    if (separator == std::string::npos) {
      Serial.println("Invalid command format (missing colon).");
      return;
    }

    // Extract the pin part and the command part
    std::string pinStr = rx_message.substr(0, separator);
    std::string cmd = rx_message.substr(separator + 1);

    // Trim whitespace from the command
    cmd.erase(std::remove_if(cmd.begin(), cmd.end(), ::isspace), cmd.end());

    // Convert the pin substring to an integer
    int pin = atoi(pinStr.c_str());

    // Validate that the pin is one of our motor pins
    if (pin != MOTOR_PIN_5 && pin != MOTOR_PIN_19 && pin != MOTOR_PIN_21 && pin != MOTOR_PIN_4) {
      Serial.println("Invalid motor pin.");
      return;
    }

    Serial.printf("  Pin parsed: %d\n", pin);
    Serial.printf("  Command parsed: \"%s\"\n", cmd.c_str());

    // Execute the command
    if (cmd == "1") {
      digitalWrite(pin, HIGH);
      Serial.printf("Motor ON at pin %d\n", pin);
    } else if (cmd == "0") {
      digitalWrite(pin, LOW);
      Serial.printf("Motor OFF at pin %d\n", pin);
    } else {
      Serial.println("Invalid command received.");
    }
  }
};

/* Global Variables */
// List of all the masters. It will be populated when a new master is registered
std::vector<ESP_NOW_Peer_Class> masters;

/* Callbacks */
// Called when a new broadcast peer (master) is discovered
void register_new_master(const esp_now_recv_info_t *info, const uint8_t *data, int len, void *arg) {
  // If it is a broadcast message, register the sending peer as a master
  if (memcmp(info->des_addr, ESP_NOW.BROADCAST_ADDR, 6) == 0) {
    Serial.printf("Unknown peer " MACSTR " sent a broadcast message\n", MAC2STR(info->src_addr));
    Serial.println("Registering the peer as a master");

    ESP_NOW_Peer_Class new_master(info->src_addr, ESPNOW_WIFI_CHANNEL, WIFI_IF_STA, NULL);

    masters.push_back(new_master);
    if (!masters.back().add_peer()) {
      Serial.println("Failed to register the new master");
      return;
    }
  } else {
    // We only handle broadcast here; ignore unicast from unknown peers
    log_v("Received a unicast message from " MACSTR, MAC2STR(info->src_addr));
    log_v("Ignoring the message");
  }
}

/* Main */
void setup() {
  Serial.begin(9600);
  Serial.println("Starting BLE Motor Control!");

  // Initialize pins for motors
  pinMode(MOTOR_PIN_5, OUTPUT);
  pinMode(MOTOR_PIN_19, OUTPUT);
  pinMode(MOTOR_PIN_21, OUTPUT);
  pinMode(MOTOR_PIN_4, OUTPUT);
  digitalWrite(MOTOR_PIN_5, LOW);
  digitalWrite(MOTOR_PIN_19, LOW);
  digitalWrite(MOTOR_PIN_21, LOW);
  digitalWrite(MOTOR_PIN_4, LOW);

  // Initialize the Wi-Fi module
  WiFi.mode(WIFI_STA);
  WiFi.setChannel(ESPNOW_WIFI_CHANNEL);

  // Wait until the STA interface is started
  while (!WiFi.STA.started()) {
    delay(100);
  }

  Serial.println("ESP-NOW Example - Broadcast Slave");
  Serial.println("Wi-Fi parameters:");
  Serial.println("  Mode: STA");
  Serial.println("  MAC Address: " + WiFi.macAddress());
  Serial.printf("  Channel: %d\n", ESPNOW_WIFI_CHANNEL);

  // Initialize the ESP-NOW protocol
  if (!ESP_NOW.begin()) {
    Serial.println("Failed to initialize ESP-NOW");
    Serial.println("Rebooting in 5 seconds...");
    delay(5000);
    ESP.restart();
  }

  // Register the callback for new peers
  ESP_NOW.onNewPeer(register_new_master, NULL);

  Serial.println("Setup complete. Waiting for a master to broadcast a message...");
}

void loop() {
  // Just wait; messages will come in via onReceive callback
  delay(1000);
}
