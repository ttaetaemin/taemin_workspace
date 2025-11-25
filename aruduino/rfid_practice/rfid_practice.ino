#include <SPI.h>
#include <MFRC522.h>
#include <List.hpp>

#define RST_PIN    9
#define SS_PIN     10

#define RED_PIN    3  // blue
#define GREEN_PIN  5
#define BLUE_PIN   6  // red

List<MFRC522::Uid> tag_list;
MFRC522 mfrc522(SS_PIN, RST_PIN);

// 깜빡임 상태
bool isBlinking = false;
unsigned long lastBlinkTime = 0;
int blinkCount = 0;
bool ledOn = false;
enum BlinkColor { NONE, BLUE, RED };
BlinkColor currentColor = NONE;

void setLEDColor(int r, int g, int b) {
  analogWrite(RED_PIN,   r);
  analogWrite(GREEN_PIN, g);
  analogWrite(BLUE_PIN,  b);
}

void blinkLED(BlinkColor color) {
  // 이전 깜빡임을 덮어쓰고 새로 시작
  isBlinking = true;
  blinkCount = 0;
  ledOn = false;
  currentColor = color;
  lastBlinkTime = millis();
}

void updateLED() {
  static bool ledSet = false;

  if (!isBlinking) {
    if (!ledSet) {
      setLEDColor(255, 255, 255); // 기본 흰색 유지
      ledSet = true;
    }
    return;
  } else {
    ledSet = false;
  }

  if (millis() - lastBlinkTime >= 200) {
    lastBlinkTime = millis();
    ledOn = !ledOn;

    if (ledOn) {
      if (currentColor == BLUE)
        setLEDColor(0, 0, 255);  // 파란색
      else if (currentColor == RED)
        setLEDColor(255, 0, 0);  // 빨간색
    } else {
      setLEDColor(0, 0, 0); // 꺼짐
      blinkCount++;
      if (blinkCount >= 3) {
        isBlinking = false;
        currentColor = NONE;
      }
    }
  }
}

void setup() {
  Serial.begin(9600);
  while (!Serial);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  setLEDColor(255, 255, 255); // 기본 흰색

  SPI.begin();
  mfrc522.PCD_Init();
  delay(4);
  mfrc522.PCD_DumpVersionToSerial();
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
}

void loop() {
  updateLED(); // LED 상태 갱신은 항상

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  Serial.print("Read UID Tag : ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  bool registered = false;
  for (int i = 0; i < tag_list.getSize(); i++) {
    if (memcmp(tag_list.get(i).uidByte, mfrc522.uid.uidByte, 4) == 0) {
      registered = true;
      break;
    }
  }

  if (!registered) {
    tag_list.addLast(mfrc522.uid);
    Serial.println(">> New card registered!");
    blinkLED(BLUE); // 신규 등록: 빨간색 깜빡임
  } else {
    Serial.println(">> Recognized card");
    blinkLED(RED); // 기존 등록: 파란색 깜빡임
  }

  Serial.print("Registered Tag List (");
  Serial.print(tag_list.getSize());
  Serial.println(") :");

  for (int i = 0; i < tag_list.getSize(); i++) {
    for (byte j = 0; j < 4; j++) {
      Serial.print(tag_list.get(i).uidByte[j] < 0x10 ? " 0" : " ");
      Serial.print(tag_list.get(i).uidByte[j], HEX);
    }
    Serial.println();
  }

  mfrc522.PICC_HaltA(); // 통신 종료
}
