
void setup() {
  Serial.begin(9600); // Start serial communication
  pinMode(5, OUTPUT); // Set pin 12 as output
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read(); // Read command from serial
    if (command == '1') {
      digitalWrite(5, HIGH); // Turn pin 12 on
    } else if (command == '0') {
      digitalWrite(5, LOW); // Turn pin 12 off
    }
  }
}