#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define LED_PIN LED_BUILTIN  // Use the built-in LED

// UUIDs for the service and characteristic
#define SERVICE_UUID "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-123456789abc"

BLECharacteristic *pCharacteristic;
bool ledState = false;  // Current state of the LED
unsigned long lastPingTime = 0;
const unsigned long connectionTimeout = 10000; // 10 seconds timeout for connection

class LEDCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    std::string value = std::string((const char *)pCharacteristic->getValue().c_str());  // Convert value properly
    Serial.print("Received value: ");
    Serial.println(value.c_str());

    if (!value.empty()) {
      if (value == "1") {  // Turn LED on
        ledState = true;
        Serial.println("LED turned ON");
      } else if (value == "0") {  // Turn LED off
        ledState = false;
        Serial.println("LED turned OFF");
      } else if (value == "ping") {
        lastPingTime = millis(); // Update the last ping time
        Serial.println("Ping received.");
      } else {
        Serial.println("Invalid command received");
      }
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE LED control!");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);  // Ensure LED starts off

  // Initialize BLE
  BLEDevice::init("ESP32_Light_Controller");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );

  pCharacteristic->setCallbacks(new LEDCallbacks());

  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();

  Serial.println("BLE LED control is ready!");
  lastPingTime = millis(); // Initialize the last ping time
}

void loop() {
  if (ledState) {
    digitalWrite(LED_PIN, HIGH);  // Turn the LED on
  } else {
    digitalWrite(LED_PIN, LOW);  // Turn the LED off
  }

  // Check for connection timeout
  if (millis() - lastPingTime > connectionTimeout) {
    Serial.println("Connection lost. No ping received within timeout period.");
    lastPingTime = millis(); // Reset the timer to avoid repeated messages
  }

  delay(100);  // Small delay to allow for BLE processing
}
