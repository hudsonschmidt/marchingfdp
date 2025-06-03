#include <Wire.h>
//This code tests for I2C devices to check if IMU is recognized and connected 
void setup() {
  Serial.begin(115200);
  Wire.begin();
}

void loop() {
  byte error, address;
  int nDevices = 0;
  delay(5000);
  Wire.beginTransmission(0x69);
  Serial.println("Scanning for I2C devices ...");
  for (address = 0x01; address < 0x7f; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("I2C device found at address 0x%02X\n", address);
      nDevices++;
    } else if (error != 2) {
      Serial.printf("Error %d at address 0x%02X\n", error, address);
    }
    //Serial.println(Wire.endTransmission());
  }
  if (nDevices == 0) {
    Serial.println("No I2C devices found");
  }
}