const int LED_PIN = 9;

// int min = 1024;
// int max = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int light = analogRead(A0);

  int output = map(light, 650, 820, 0, 255);

  if (output < 0)
  {
    output = 0;
  }

  if (output > 255)
  {
    output = 255;
  }



  Serial.print(light);
  Serial.print(", ");
  Serial.println(output);

  analogWrite(LED_PIN, output);
  // if (light < min) {
  //   min = light;
  // }

  // if (light > max) {
  //   max = light;
  // }

  // Serial.print(min);
  // Serial.print(",");
  // Serial.println(max);

  // for (int i = 0; i < 255; i++) {
  //   analogWrite(LED_PIN, i);
  //   delay(10);
  // }

  // for (int i = 255; i > 0; i--) {
  //   analogWrite(LED_PIN, i);
  //   delay(5);
  // }
}