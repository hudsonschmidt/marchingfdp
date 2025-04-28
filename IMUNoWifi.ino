/*
 * This Arduino Sketch initializes the ICM20948 sensor, reads pitch, roll,
 * yaw, and azimuth data, and outputs these values via the serial monitor.
 */

 #include <Wire.h>
 #include <Adafruit_ICM20948.h>
 
 Adafruit_ICM20948 icm;
 
 void setup() {
   Serial.begin(115200);
   while (!Serial) delay(10); // Wait for Serial to be ready
 
   Serial.println("ICM20948 Test");
 
   if (!icm.begin_I2C()) {
     Serial.println("Failed to find ICM20948 chip");
     while (1) { delay(10); }
   }
   Serial.println("ICM20948 Found!");
 
   icm.setAccelRange(ICM20948_ACCEL_RANGE_2_G);
   icm.setGyroRange(ICM20948_GYRO_RANGE_250_DPS);
   icm.setMagDataRate(AK09916_MAG_DATARATE_100_HZ);
 }
 
 void loop() {
   sensors_event_t accel;
   sensors_event_t gyro;
   sensors_event_t mag;
   sensors_event_t temp;
 
   icm.getEvent(&accel, &gyro, &temp, &mag);
 
   float pitch = atan2(accel.acceleration.y, accel.acceleration.z) * 180 / PI;
   float roll = atan2(-accel.acceleration.x, sqrt(accel.acceleration.y * accel.acceleration.y + accel.acceleration.z * accel.acceleration.z)) * 180 / PI;
   float yaw = atan2(mag.magnetic.y, mag.magnetic.x) * 180 / PI;
   float azimuth = atan2(mag.magnetic.z, sqrt(mag.magnetic.x * mag.magnetic.x + mag.magnetic.y * mag.magnetic.y)) * 180 / PI;
 
   Serial.print("Pitch: "); Serial.print(pitch);
   Serial.print(" Roll: "); Serial.print(roll);
   Serial.print(" Yaw: "); Serial.print(yaw);
   Serial.print(" Azimuth: "); Serial.println(azimuth);
 
   delay(500);
 }