#include <SPI.h>
#include <MFRC522.h>

const int RST_PIN = 9;
const int SS_PIN = 10;
MFRC522 rc522(SS_PIN, RST_PIN);

// const int TOTAL_INDEX = 60;
const int TOTAL_INDEX = 10;

MFRC522::MIFARE_Key key;

// 🔧 수정됨: UID 저장용 변수
byte currentUID[4] = {0x00, 0x00, 0x00, 0x00}; 
bool cardDetected = false;

MFRC522::StatusCode checkAuth(int index)
{
  // 새 Uid 구조체에 currentUID를 복사
  MFRC522::Uid tempUid;
  memcpy(tempUid.uidByte, currentUID, 4);
  tempUid.size = 4;

  MFRC522::StatusCode status =
    rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &tempUid);
  return status;
}


MFRC522::StatusCode readData(int index, byte* data) 
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  byte buffer[18];
  byte length = 18;
  status = rc522.MIFARE_Read(index, buffer, &length);
  if (status == MFRC522::STATUS_OK)
  {
    memcpy(data, buffer, 4);
  }

  return status;
}

MFRC522::StatusCode writeData(int index, byte* data, int length) 
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, data, length);

  status = rc522.MIFARE_Write(index, buffer, 16);
  return status;
}

void setup() 
{
  Serial.begin(9600);

  SPI.begin();
  rc522.PCD_Init();

  for (int i = 0; i < 6; i++)
  {
    key.keyByte[i] = 0xFF;
  }
}

void loop() 
{
  int recv_size = 0;
  char recv_buffer[16];

  if (Serial.available() > 0)
  {
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 16);
  }

  // 🔧 수정됨: 카드 감지되면 currentUID 저장
  if (rc522.PICC_IsNewCardPresent() && rc522.PICC_ReadCardSerial()) {
    memcpy(currentUID, rc522.uid.uidByte, 4);
    cardDetected = true;
  }

  if (recv_size > 0)
  {
    char cmd[2];
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 2);

    char send_buffer[16];
    memset(send_buffer, 0x00, sizeof(send_buffer));
    memcpy(send_buffer, cmd , 2);

    // 🔧 수정됨: UID 비교 대상 → currentUID
    if (strncmp(cmd, "GS", 2) != 0)
    {
      if (!cardDetected || memcmp(recv_buffer + 2, currentUID, 4) != 0)
      {
        memset(send_buffer + 2, 0xFB, 1);
        Serial.write(send_buffer, 3);
        Serial.println();
        return;
      }
    }

    MFRC522::StatusCode status = MFRC522::STATUS_ERROR;

    // 🔧 수정됨: 카드 없어도 계속 처리 가능하도록
    if (strncmp(cmd, "GS", 2) == 0 && cardDetected)
    {
      memset(send_buffer + 2, MFRC522::STATUS_OK, 1);
      memcpy(send_buffer + 3, currentUID, 4);
      Serial.write(send_buffer, 7);
    }
    else if (strncmp(cmd, "GT", 2) == 0 && cardDetected)
    {
      byte total[4];
      memset(total, 0X00, 4);
      status = readData(TOTAL_INDEX, total);

      memset(send_buffer + 2, status, 1);
      memcpy(send_buffer + 3, total, 4);
      Serial.write(send_buffer, 7);
    }
    else if (strncmp(cmd, "ST", 2) == 0 && cardDetected)
    {
      byte total[4];
      memset(total, 0X00, sizeof(total));
      memcpy(total, recv_buffer + 6, 4);

      status = writeData(TOTAL_INDEX, total, 4);

      memset(send_buffer + 2, status, 1);
      Serial.write(send_buffer, 3);
    }
    else
    {
      memset(send_buffer + 2, 0xFA, 1); // 카드 없음
      Serial.write(send_buffer, 3);
    }

    Serial.println();
  }
}
