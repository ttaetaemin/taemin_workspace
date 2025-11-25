#include <WiFi.h>
#include <ESP32Servo.h>



const char *ssid = "AIE_509_2.4G";
const char *password = "addinedu_class1";

Servo servo;
const int servo_pin = 5;

WiFiServer server(80);

// ✅ 컴파일 에러 수정: 구조체 정의 추가 (필수)
struct protocol {
  int pin;
  int status;
};

void setup() {

  servo.attach(servo_pin);

  pinMode(21, OUTPUT);
  pinMode(22, OUTPUT);
  pinMode(23, OUTPUT);

  Serial.begin(115200);
  Serial.println("ESP32 Web Server Start");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.print("Client Connected : ");
    Serial.println(client.remoteIP());
    struct protocol p;
    while (client.connected()) {
      char data[8];

      while (client.available() > 0) {
        client.readBytes(data, 8);
        memcpy(&p, data, sizeof(p)); 

        if (p.pin == servo_pin)
        {
          servo.write(p.status);
        }
        else
        {
          digitalWrite(p.pin, p.status);
        }

        Serial.println(p.pin);
        Serial.println(p.status);

        client.write(data, 8);
      } 
      delay (10);
    }
 
  }
}
