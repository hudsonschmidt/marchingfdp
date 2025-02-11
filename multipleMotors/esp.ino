#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// UUIDs for the BLE service and characteristic
#define SERVICE_UUID         "12345678-1234-1234-1234-123456789abc"
#define CHARACTERISTIC_UUID  "87654321-4321-4321-4321-123456789abc"

// Define the two motor control pins
const int MOTOR_PIN_5  = 5;
const int MOTOR_PIN_19 = 19;
const int MOTOR_PIN_21 = 21;
const int MOTOR_PIN_4 = 4;

unsigned long lastPingTime = 0;
const unsigned long connectionTimeout = 10000; // 10 seconds timeout for "ping"
BLEServer *pServer = nullptr;
BLEAdvertising *pAdvertising = nullptr;
bool deviceConnected = false;

class MotorCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    std::string value = std::string((const char *)pCharacteristic->getValue().c_str());
    Serial.print("Received value: ");
    Serial.println(value.c_str());

    if (!value.empty()) {
      if (value == "ping") {
        lastPingTime = millis();
        Serial.println("Ping received.");
        return;
      }
      
      size_t separator = value.find(':');
      if (separator == std::string::npos) {
        Serial.println("Invalid command format.");
        return;
      }
      
      std::string pinStr = value.substr(0, separator);
      std::string cmd = value.substr(separator + 1);
      
      int pin = atoi(pinStr.c_str());
      if (pin != MOTOR_PIN_5 && pin != MOTOR_PIN_19) {
        Serial.println("Invalid motor pin.");
        return;
      }

      if (cmd == "1") {
        digitalWrite(pin, HIGH);
        Serial.print("Motor ON at pin ");
        Serial.println(pin);
      } else if (cmd == "0") {
        digitalWrite(pin, LOW);
        Serial.print("Motor OFF at pin ");
        Serial.println(pin);
      } else {
        Serial.println("Invalid command received.");
      }
    }
  }
};

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) override {
    deviceConnected = true;
    Serial.println("Client connected.");
  }

  void onDisconnect(BLEServer* pServer) override {
    deviceConnected = false;
    Serial.println("Client disconnected. Restarting advertising...");
    pAdvertising->start();
  }
};

void setup() {
  Serial.begin(9600);
  Serial.println("Starting BLE Motor Control!");

  pinMode(MOTOR_PIN_5, OUTPUT);
  pinMode(MOTOR_PIN_19, OUTPUT);
  pinMode(MOTOR_PIN_21, OUTPUT);
  pinMode(MOTOR_PIN_4, OUTPUT);
  digitalWrite(MOTOR_PIN_5, LOW);
  digitalWrite(MOTOR_PIN_19, LOW);
  digitalWrite(MOTOR_PIN_21, LOW);
  digitalWrite(MOTOR_PIN_4, LOW);

  BLEDevice::init("ESP32_Motor_Controller");
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE
  );

  pCharacteristic->setCallbacks(new MotorCallbacks());
  
  pService->start();
  pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  pAdvertising->start();

  Serial.println("BLE Motor Control is ready!");
  lastPingTime = millis();
}

void loop() {
  if (millis() - lastPingTime > connectionTimeout) {
    Serial.println("Connection lost. No ping received within timeout period.");
    lastPingTime = millis();
  }
  delay(100);
}