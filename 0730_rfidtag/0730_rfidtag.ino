#include <SPI.h>
#include <MFRC522.h>

const int RST_PIN = 9;
const int SS_PIN = 10;

MFRC522 rc522(SS_PIN, RST_PIN);

struct TagData
{
  char name[16];
  long total;
  long payment;
};

void toBytes(byte* buffer, int data, int offset = 0)
{
  buffer[offset] = data & 0xFF;
  buffer[offset + 1] = (data >> 8) & 0xFF;
}

int toInteger(byte* buffer, int offset = 0)
{
  return (buffer[offset + 1]<< 8 | buffer[offset]);
}

MFRC522::StatusCode checkAuth(int index, MFRC522::MIFARE_Key key)
{
  MFRC522::StatusCode status = 
  rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid));

  if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Authentication Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));
  }

  return status;
}

MFRC522::StatusCode writeString(int index, MFRC522::MIFARE_Key key, String data)
{
    //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  char buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  data.toCharArray(buffer, data.length() +1);

  //write data
  status = rc522.MIFARE_Write(index, (byte*)&buffer, 16);
  if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Write Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));
  }

  return status;
}

MFRC522::StatusCode writeInteger(int index, MFRC522::MIFARE_Key key, int data)
{
    //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  toBytes(buffer, data);

  //write data
  status = rc522.MIFARE_Write(index, buffer, sizeof(buffer));
  if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Write Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));
  }

  return status;
}

MFRC522::StatusCode writeTagData(int index, MFRC522::MIFARE_Key key, TagData data)
{
    //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  byte buffer[32];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, &data, sizeof(data));

  //write data

  for (int i = 0; i < 2; i++)
  {
    status = rc522.MIFARE_Write(index + i, buffer + (i * 16), 16); //sizeof(buffer));
    if (status != MFRC522::STATUS_OK)
    {
      Serial.print("Write Failed : ");
      Serial.println(rc522.GetStatusCodeName(status));
    }
  }
  return status;
}

MFRC522::StatusCode readString(int index, MFRC522::MIFARE_Key key, String& data)
{
  //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  // read data
  byte buffer[18];
  byte length = 18;

  status = rc522.MIFARE_Read(index, buffer, &length);
   if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Read Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  else 
  {
    data = String((char*)buffer);
  }
  
  return status;
}

MFRC522::StatusCode readInteger(int index, MFRC522::MIFARE_Key key, int& data)
{
  //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  // read data
  byte buffer[18];
  byte length = 18;

  status = rc522.MIFARE_Read(index, buffer, &length);
   if (status != MFRC522::STATUS_OK)
  {
    Serial.print("Read Failed : ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  else 
  {
    data = toInteger(buffer);
  }
  
  return status;
}

MFRC522::StatusCode readTagData(int index, MFRC522::MIFARE_Key key, TagData& data)
{
  //check auth
  MFRC522::StatusCode status = checkAuth(index, key);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }

  // read data
  byte buffer[34];
  byte length = 18;

  for (int i = 0; i < 2; i++)
  {
    status = rc522.MIFARE_Read(index + i, buffer + (i * 16), &length);
    if (status != MFRC522::STATUS_OK)
    {
      Serial.print("Read Failed : ");
      Serial.println(rc522.GetStatusCodeName(status));
    }
  

  memcpy(&data, buffer, sizeof(data));
  return status;
  }
}




void setup() 
{
  // put your setup code here, to run once:
  Serial.begin(9600);

  SPI.begin();
  rc522.PCD_Init();

  Serial.println("start!");
}

void loop() 
{
  
  String cmd = "";
  if (Serial.available() > 0) {
    delay(50);
    cmd = Serial.readStringUntil('\n');
    Serial.print("cmd : ");
    Serial.println(cmd);
  } 
  else {
    return;
  }

  if (cmd == "") return;
  
  if (!rc522.PICC_IsNewCardPresent() || !rc522.PICC_ReadCardSerial()) {
    return;
  }


  // if (cmd.length() > 0)
  // {
  //   Serial.print("cmd : ");
  //   Serial.println(cmd);

  // }

  //set key value
  MFRC522::MIFARE_Key key;
  for (int i = 0; i < 6; i++) {
    key.keyByte[i] = 0xff;
  }

  MFRC522::StatusCode status = MFRC522::STATUS_ERROR;
  String s_data;
  int i_data;
  TagData t_data;
  String s_temp;


  if (cmd.length() > 0)
  {
    Serial.print("cmd : ");
    switch(cmd.charAt(0))
    {
      case 'w':
        Serial.println("write");
        switch (cmd.charAt(1))
        {
          case 's':
            Serial.println("string");
            status = writeString(60, key, "taemin");
            break;
          case 'i':
            Serial.println("integer");
            status = writeInteger(61, key, 32767);
            rc522.PICC_DumpToSerial(&(rc522.uid));
            break;
          case 't':
            Serial.println("struct");
            s_temp = "tm tag";
            s_temp.toCharArray(t_data.name, s_temp.length() + 1);
            t_data.total = 2147483647;
            t_data.payment = 2000000000;
            status = writeTagData(56, key, t_data);
            rc522.PICC_DumpToSerial(&(rc522.uid));
            break;
          default:
            Serial.println("unknown type");
            status = MFRC522::STATUS_ERROR;
            break;
        }
        break;
      case 'r':
        Serial.println("read");
        switch (cmd.charAt(1))
        {
          case 's':
            Serial.println("string");
            status = readString(60, key, s_data);
            Serial.println(s_data);
            break;
          case 'i':
            Serial.println("integer");
            status = readInteger(61, key, i_data);
            Serial.println(i_data);
            break;
          case 't':
            Serial.println("struct");
            status = readTagData(56, key, t_data);
            Serial.print(" name : ");         Serial.println(String(t_data.name));
            Serial.print(" total : ");        Serial.println(t_data.total);
            Serial.print(" payment : ");      Serial.println(t_data.payment);
            break;
          default:
            Serial.println("unknown type");
            status = MFRC522::STATUS_ERROR;
            break;
        }
        break;
      default:
        Serial.println("unknown");
        status = MFRC522::STATUS_ERROR;
        break;
    }
   
  }


  if (status == MFRC522::STATUS_OK)
  {
    Serial.println("success!");
  }
  cmd = "";
  delay(500);

}
  


 
