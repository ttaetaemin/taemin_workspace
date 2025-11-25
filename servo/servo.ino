#include <Servo.h>

int pos = 0;
Servo servo;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  servo.attach(9);
}

void loop() {
  // put your main code here, to run repeatedly:
  // while (Serial.available() > 0)
  // {
  //   String input = Serial.readStringUntil('\n');
  //   float pos = input.toFloat();

  //   Serial.println(pos);
  //   // Serial.println(pos * 2);
  //   servo.write(pos);
  // }

  for (pos = 0; pos <= 180; pos++)
  {
    servo.write(pos);
    delay(15);
  }

  for (pos = 180; pos >= 0; pos--)
  {
    servo.write(pos);
    delay(15);
  }
}
