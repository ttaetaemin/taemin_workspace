const int SOUND_PIN = A0;
const int ledPins[8] = {2, 3, 4, 5, 6, 7, 8, 9};

void setup() 
{
  Serial.begin(9600);
  for (int i = 0; i < 8; i++) 
  {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() 
{
  int sound = analogRead(SOUND_PIN);
  Serial.println(sound);

  sound = constrain(sound, 50, 300);
  int level = map(sound, 50, 300, 0, 7);
  level = constrain(level, 0, 7);

  // 아래에서 위로 점등
  for (int i = 0; i < level; i++) {
    digitalWrite(ledPins[i], HIGH);
    delay(50);  // LED 올라가는 속도 조절
  }

  // 잠시 유지
  delay(100);

  // 위에서 아래로 소등
  for (int i = level - 1; i >= 0; i--) {
    digitalWrite(ledPins[i], LOW);
    delay(50);  // LED 내려가는 속도 조절
  }

  delay(100);  // 다음 측정까지 약간 쉬기
}
