const int PIR_PIN = 2;
const int BLUE_PIN = 4;

unsigned long ledOffTime = 0;
bool ledOn = false;

void setup() {
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);
  pinMode(BLUE_PIN, OUTPUT);
}

void loop() {
  int input = digitalRead(PIR_PIN);
  unsigned long now = millis();

  // 1. 감지되면 타이머 5초 연장 (LED 켜짐)
  if (input == HIGH) {
    ledOffTime = now + 5000;  // 현재 시간 + 5초
    ledOn = true;
    Serial.println("Motion Detected - Timer Extended");
  }

  // 2. LED ON 상태 유지
  if (ledOn && now < ledOffTime) {
    digitalWrite(BLUE_PIN, HIGH);
    Serial.println("LED ON (active)");
    if (input == HIGH) {
      ledOffTime = now + 5000;  // 현재 시간 + 5초
      ledOn = true;
      Serial.println("Motion Detected - Timer Extended");
    }
  }

  // 3. 5초가 지나면 LED OFF
  else if (ledOn && now >= ledOffTime) {
    digitalWrite(BLUE_PIN, LOW);
    ledOn = false;
    Serial.println("LED OFF (timeout)");
  }

  delay(100);
}


// const int PIR_PIN = 2;
// const int BLUE_PIN = 4;

// unsigned long ledOffTime = 0;
// bool ledOn = false;

// void setup() {
//   Serial.begin(9600);
//   pinMode(PIR_PIN, INPUT);
//   pinMode(BLUE_PIN, OUTPUT);
// }

// void loop() {
//   int input = digitalRead(PIR_PIN);
//   unsigned long now = millis();

//   // 1. 감지 시: 5초 타이머 시작
//   if (input == HIGH && !ledOn) {
//     ledOffTime = now;
//     ledOn = true;
//     Serial.println("Motion Detected");
//   }

//   // 2. 감지 이후 5초 동안은 LED 켜기
//   if (ledOn && now < ledOffTime + 5000) {
//     digitalWrite(BLUE_PIN, HIGH);
//     Serial.println("LED ON (within 5s)");
//   }

//   // 3. 5초 지나면 LED 끄고, 다시 감지 가능하도록 리셋
//   else if (ledOn && now >= ledOffTime + 5000) {
//     digitalWrite(BLUE_PIN, LOW);
//     ledOn = false;  // 다시 감지 가능하도록 초기화
//     Serial.println("LED OFF (after 5s)");
//   }

//   delay(100);
// }

