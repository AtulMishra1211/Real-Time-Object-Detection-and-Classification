#include <Servo.h>

Servo servoVer; // Vertical Servo
Servo servoHor; // Horizontal Servo
int x;
int y;
int prevX;
int prevY;

void setup() {
  Serial.begin(9600);
  servoVer.attach(9); // Attach Vertical Servo to Pin 9
  servoHor.attach(10); // Attach Horizontal Servo to Pin 10
  servoVer.write(0); // Initialize to middle position
  servoHor.write(90); // Initialize to middle position
}

void Pos() {
  if (prevX != x || prevY != y) {
    // Reverse the pan direction if needed
    int servoX = map(x, 0, 640, 0, 179); // Reverse mapping for pan
    int servoY = map(y, 0, 480, 30, 0); // Adjust tilt range

    // Ensure values are within servo limits
    servoX = constrain(servoX, 0, 179);
    servoY = constrain(servoY, 0, 60);

    servoHor.write(servoX);
    servoVer.write(servoY);

    prevX = x;
    prevY = y;
  }
}

void loop() {
  if (Serial.available() > 0) {
    if (Serial.read() == 'X') {
      x = Serial.parseInt();
      if (Serial.read() == 'Y') {
        y = Serial.parseInt();
        Pos();
      }
    }
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}
