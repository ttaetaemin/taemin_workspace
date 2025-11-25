#include <Servo.h>

Servo servo;

const int BUTTON_PIN = 2;
int currentPos = 0;         // 초기 위치
bool lastButtonState = LOW;
bool increasing = true;     // true면 +10, false면 -10

void setup() {
  servo.attach(9);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // 버튼 핀을 내부 풀업으로 설정
  servo.write(currentPos);            // 초기 위치로 이동
}

void loop() {
  bool buttonState = digitalRead(BUTTON_PIN);

  // 버튼이 눌렸을 때만 반응
  if (lastButtonState == HIGH && buttonState == LOW) {
    if (increasing) {
      currentPos += 10;
      if (currentPos >= 180) {
        currentPos = 180;
        increasing = false;  // 방향 전환
      }
    } else {
      currentPos -= 10;
      if (currentPos <= 0) {
        currentPos = 0;
        increasing = true;   // 방향 전환
      }
    }

    servo.write(currentPos);  // 위치 이동
    delay(200);               // 디바운스 지연
  }

  lastButtonState = buttonState;
}
