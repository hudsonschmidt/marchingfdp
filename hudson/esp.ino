#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUIDs for the BLE service and characteristic
#define SERVICE_UUID "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID "87654321-4321-4321-4321-123456789abc"

// Change this to the pin you want to control the motor with
#define MOTOR_PIN 5

BLECharacteristic *pCharacteristic;
unsigned long lastPingTime = 0;
const unsigned long connectionTimeout = 10000; // 10 seconds timeout for "ping"

class MotorCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    // Convert the BLE value to a std::string
    std::string value = std::string((const char *)pCharacteristic->getValue().c_str());
    Serial.print("Received value: ");
    Serial.println(value.c_str());

    if (!value.empty()) {
      if (value == "1") {
        digitalWrite(MOTOR_PIN, HIGH); // Turn the motor ON
        Serial.println("Motor turned ON");
      } 
      else if (value == "0") {
        digitalWrite(MOTOR_PIN, LOW);  // Turn the motor OFF
        Serial.println("Motor turned OFF");
      } 
      else if (value == "ping") {
        lastPingTime = millis();       // Update the last ping time
        Serial.println("Ping received.");
      } 
      else {
        Serial.println("Invalid command received");
      }
    }
  }
};

void setup() {
  Serial.begin(9600); // Match your desired serial rate
  Serial.println("Starting BLE Motor Control!");

  pinMode(MOTOR_PIN, OUTPUT);
  digitalWrite(MOTOR_PIN, LOW); // Ensure the motor is OFF initially

  // Initialize BLE
  BLEDevice::init("ESP32_Motor_Controller");
  BLEServer *pServer = BLEDevice::createServer();

  // Create service and characteristic
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );

  // Assign our callback class to handle writes
  pCharacteristic->setCallbacks(new MotorCallbacks());
  
  // Start the service and begin advertising
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();

  Serial.println("BLE Motor Control is ready!");
  lastPingTime = millis(); // Initialize last ping time
}

void loop() {
  // Check for a connection timeout (if you're using the "ping" command)
  if (millis() - lastPingTime > connectionTimeout) {
    Serial.println("Connection lost. No ping received within timeout period.");
    lastPingTime = millis(); // Reset to avoid repeated messages
  }

  delay(100); // Small delay for BLE processing
}
