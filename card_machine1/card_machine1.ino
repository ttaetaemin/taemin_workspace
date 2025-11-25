#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
#define TOTAL_INDEX 4  // 총액 저장할 블럭

MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

byte currentUID[4] = {0};
bool cardDetected = false;

// ----------------- 유틸 ------------------

void dumpByteArray(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
}

bool isSameUID(byte *a, byte *b) {
  for (int i = 0; i < 4; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
}

// ----------------- RFID 블럭 작업 ------------------

MFRC522::StatusCode checkAuth(byte block) {
  return rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(rfid.uid));
}

MFRC522::StatusCode readBlock(byte block, byte *data_out) {
  MFRC522::StatusCode status = checkAuth(block);
  if (status != MFRC522::STATUS_OK) return status;

  byte buffer[18];
  byte len = 18;
  status = rfid.MIFARE_Read(block, buffer, &len);
  if (status == MFRC522::STATUS_OK) {
    memcpy(data_out, buffer, 4);  // 앞의 4바이트만 사용
  }
  return status;
}

MFRC522::StatusCode writeBlock(byte block, byte *data_in, byte length) {
  MFRC522::StatusCode status = checkAuth(block);
  if (status != MFRC522::STATUS_OK) return status;

  byte buffer[16] = {0};
  memcpy(buffer, data_in, length);
  return rfid.MIFARE_Write(block, buffer, 16);
}

void resetBlock(byte block) {
  if (checkAuth(block) != MFRC522::STATUS_OK) return;
  byte buffer[16] = {0};
  rfid.MIFARE_Write(block, buffer, 16);
}

// ----------------- 초기화 ------------------

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();

  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  Serial.println("Ready");
}

// ----------------- 메인 루프 ------------------

void loop() {
  static char recv[32];
  static int recv_len = 0;

  // 카드 감지
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    memcpy(currentUID, rfid.uid.uidByte, 4);
    cardDetected = true;
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }

  // 명령 수신
  if (Serial.available()) {
    recv_len = Serial.readBytesUntil('\n', recv, sizeof(recv));
    recv[recv_len] = '\0';

    char cmd[3] = {recv[0], recv[1], '\0'};
    char response[16] = {cmd[0], cmd[1], 0x00};

    // === 카드 감지용 ===
    if (strcmp(cmd, "GS") == 0) {
      if (!cardDetected) {
        response[2] = 0xFA;
        Serial.write(response, 3);
      } else {
        response[2] = 0x00;
        memcpy(response + 3, currentUID, 4);
        Serial.write(response, 7);
      }
      Serial.println();
      return;
    }

    // === 카드 UID 검증 ===
    if (!cardDetected || !isSameUID((byte*)(recv + 2), currentUID)) {
      response[2] = (!cardDetected) ? 0xFA : 0xFB;
      Serial.write(response, 3);
      Serial.println();
      return;
    }

    // === GET ===
    if (strcmp(cmd, "GT") == 0) {
      byte data[4] = {0};
      MFRC522::StatusCode s = readBlock(TOTAL_INDEX, data);
      response[2] = s;
      memcpy(response + 3, data, 4);
      Serial.write(response, 7);
    }

    // === SET ===
    else if (strcmp(cmd, "ST") == 0) {
      byte data[4];
      memcpy(data, recv + 6, 4);
      MFRC522::StatusCode s = writeBlock(TOTAL_INDEX, data, 4);
      response[2] = s;
      Serial.write(response, 3);
    }

    // === RESET ===
    else if (strcmp(cmd, "RS") == 0) {
      resetBlock(TOTAL_INDEX);
      response[2] = 0x00;
      Serial.write(response, 3);
    }

    // === UNKNOWN ===
    else {
      response[2] = 0xFE;
      Serial.write(response, 3);
    }

    Serial.println();
  }
}
