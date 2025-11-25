#include <SPI.h>
#include <MFRC522.h>

const int RST_PIN = 9;
const int SS_PIN = 10;
MFRC522 rc522(SS_PIN, RST_PIN);


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  SPI.begin();
  rc522.PCD_Init();

  Serial.println("start!");
}

void loop() 
{
  // put your main code here, to run repeatedly:
  String cmd = "";
  while (Serial.available() > 0)
  {
    cmd = Serial.readStringUntil('\n');
  }

  if (!rc522.PICC_IsNewCardPresent()) {
    return;
  }

  if (!rc522.PICC_ReadCardSerial()){
    return;
  }

  if (cmd.length() > 0 && cmd == "w")
  {
    Serial.print("cmd : ");
    Serial.print(cmd);
  }
  else 
  {
    return;
  }

  const int index = 60;
  MFRC522::StatusCode status;

//set key value
  MFRC522::MIFARE_Key key;
  for (int i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

// check auth
  status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid));
  if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Authentication Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));

    return;
  }

// define buffer
  char data[16];
  memset(data, 0x00, sizeof(data));

// string to char array
  String name = "taemin";
  name.toCharArray(data, name.length() + 1);

// write data
  status = rc522.MIFARE_Write(index, (byte*)&data, 16);
  if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Write Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));

    return;
  }

  rc522.PICC_DumpToSerial(&(rc522.uid));
  delay(100);
}