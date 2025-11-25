#include <Servo.h>

Servo servo;

int threshhold = 80;  // 🔧 조도 차이 기준값 (낮/밤 공통)
int angle = 60;
int ground_flag = 1;
unsigned int differtime;
unsigned int down_interval = 400;
unsigned int up_interval = 50;
unsigned int dec_down_time;
unsigned int now_time;

int light = 0;
unsigned int last_light_time = 0;
const unsigned int light_interval = 500;

const int day_middle = 650;  // 🔧 낮 기준 중간값
const int night_middle = 740;  // 🔧 밤 기준 중간값
bool is_day = true;  // 🔧 낮(true) / 밤(false) 설정

void setup() {
  Serial.begin(9600);
  servo.attach(9);
  servo.write(0);
  dec_down_time = millis();
  last_light_time = millis();
}

void loop() {
  now_time = millis();

  // 0.5초마다 조도 측정
  if (now_time - last_light_time >= light_interval) {
    int raw_light = analogRead(A0);
    Serial.print("Raw Light: ");
    Serial.println(raw_light);

    int middle = is_day ? day_middle : night_middle;
    light = raw_light - middle;  // 🔧 차이를 부호 포함해 저장

    last_light_time = now_time;
  }

  // 22초마다 다운 딜레이 감소
  if (now_time - dec_down_time >= 22000 && down_interval >= 100) {
    dec_down_time = now_time;
    down_interval -= 50;
  }

  // 장애물 감지 → 점프
  // 낮: 조도값이 줄어들면 장애물 / 밤: 조도값이 늘어나면 장애물
  if (((is_day && light <= -threshhold) || (!is_day && light >= threshhold)) &&
      now_time - differtime >= up_interval &&
      ground_flag == 1) {
    servo.write(angle);
    differtime = now_time;
    ground_flag = 0;
  }

  // 평지 감지 → 착지
  else if (((is_day && light > -threshhold) || (!is_day && light < threshhold)) &&
           now_time - differtime >= down_interval &&
           ground_flag == 0) {
    servo.write(0);
    differtime = now_time;
    ground_flag = 1;
  }
}
