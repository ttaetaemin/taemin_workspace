#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

const char *ssid = "AIE_509_2.4G";
const char *password = "addinedu_class1";

// 개별 핀으로 분리
const int ledPin1 = 21;
const int ledPin2 = 22;
const int ledPin3 = 23;

AsyncWebServer server(80);

// (선택) 템플릿 치환용 — 현재 HTML에 플레이스홀더가 없으니 미사용
String processor(const String& var) {
  if (var == "STATE1") return digitalRead(ledPin1) ? "ON" : "OFF";
  if (var == "STATE2") return digitalRead(ledPin2) ? "ON" : "OFF";
  if (var == "STATE3") return digitalRead(ledPin3) ? "ON" : "OFF";
  return String();
}

const char html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
  <body>
    <center>
      <h1>Hello, ESP32 Web Server!</h1>
      <div>LED PIN 21 :
        <input type="checkbox" onchange="toggleCheckBox1(this)" />
      </div><br>
      <div>LED PIN 22 :
        <input type="checkbox" onchange="toggleCheckBox2(this)" />
      </div><br>
      <div>LED PIN 23 :
        <input type="checkbox" onchange="toggleCheckBox3(this)" />
      </div><br>
      <script>
        function toggleCheckBox1(el){
          var r=new XMLHttpRequest();
          r.open("GET", el.checked?"/on1":"/off1", true);
          r.send();
        }
        function toggleCheckBox2(el){
          var r=new XMLHttpRequest();
          r.open("GET", el.checked?"/on2":"/off2", true);
          r.send();
        }
        function toggleCheckBox3(el){
          var r=new XMLHttpRequest();
          r.open("GET", el.checked?"/on3":"/off3", true);
          r.send();
        }
      </script>
    </center>
  </body>
</html>
)rawliteral";

void setup() {
  // 핀 초기화
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
  digitalWrite(ledPin3, LOW);

  Serial.begin(115200);
  Serial.println("ESP32 Async Web Server Start");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // 루트 페이지
  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send_P(200, "text/html", html); // processor 필요 없으면 생략
    // request->send_P(200, "text/html", html, processor); // 템플릿 쓸 때
  });

  // LED 21
  server.on("/on1",  HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin1, HIGH); request->send_P(200,"text/html",html); });
  server.on("/off1", HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin1, LOW);  request->send_P(200,"text/html",html); });

  // LED 22
  server.on("/on2",  HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin2, HIGH); request->send_P(200,"text/html",html); });
  server.on("/off2", HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin2, LOW);  request->send_P(200,"text/html",html); });

  // LED 23
  server.on("/on3",  HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin3, HIGH); request->send_P(200,"text/html",html); });
  server.on("/off3", HTTP_GET, [](AsyncWebServerRequest* request){ digitalWrite(ledPin3, LOW);  request->send_P(200,"text/html",html); });

  server.begin();
  Serial.println("HTTP Server Started!");
}

void loop() {
  // Async 서버는 loop에 처리 불필요
}
