int nowFloor;
int called; // 0: stop 1: move
int mode; // 0: up 1: down
const int ELEVATOR_LED_PINS[] = {2, 3, 4, 5, 6, 7, 8};
const int BUTTON_PINS[] = {A0, A1, A2};
const int BUTTON_LED_PINS[] = {9, 10, 11};
int lightIndex;

int firstButtonClicked;
int secondButtonClicked;
int thirdButtonClicked;

int firstButtonStatus;
int secondButtonStatus;
int thirdButtonStatus;


void setup()
{
  nowFloor = 1;
  called = 0;
  mode = 0;
  lightIndex = 0;

  for (int i = 0; i < sizeof(BUTTON_PINS); i++)
  {
    pinMode(BUTTON_PINS[i], INPUT);
  }
  for (int i = 0; i < sizeof(ELEVATOR_LED_PINS); i++)
  {
    pinMode(ELEVATOR_LED_PINS[i], OUTPUT);
  }
  for (int i = 0; i < sizeof(BUTTON_LED_PINS); i++)
  {
  
    pinMode(BUTTON_LED_PINS[i], OUTPUT);
  }

  digitalWrite(ELEVATOR_LED_PINS[lightIndex], HIGH);
}


void tellButtonStatus()
{
  firstButtonClicked = digitalRead(A2);
  secondButtonClicked = digitalRead(A1);
  thirdButtonClicked = digitalRead(A0);

  if (firstButtonClicked == 1)
  {
    firstButtonStatus = !firstButtonStatus;
    delay(200);
    if (firstButtonStatus == 1)
    {
      digitalWrite(BUTTON_LED_PINS[0], HIGH);
      delay(200);
    }
  }

  if (secondButtonClicked == 1)
  {
    secondButtonStatus = !secondButtonStatus;
    delay(200);
    if (secondButtonStatus == 1)
    {
      digitalWrite(BUTTON_LED_PINS[1], HIGH);
      delay(200);
    }
  }

  if (thirdButtonClicked == 1)
  {
    thirdButtonStatus = !thirdButtonStatus;
    delay(200);
    if (thirdButtonStatus == 1)
    {
      digitalWrite(BUTTON_LED_PINS[2], HIGH);
      delay(200);
    }
  }

  if (firstButtonStatus == 1
      || secondButtonStatus == 1
      || thirdButtonStatus == 1)
  {
    called = 1;
  }
  else
  {
    called = 0;
  }
}


void moveUp()
{
  digitalWrite(ELEVATOR_LED_PINS[lightIndex], LOW);
  lightIndex++;
  delay(200);
  digitalWrite(ELEVATOR_LED_PINS[lightIndex], HIGH);
  delay(200);

  if (lightIndex % 3 == 0)
  {
    nowFloor++;
  }
}


void moveDown()
{
  digitalWrite(ELEVATOR_LED_PINS[lightIndex], LOW);
  lightIndex--;
  delay(200);
  digitalWrite(ELEVATOR_LED_PINS[lightIndex], HIGH);
  delay(200);

  if (lightIndex % 3 == 0)
  {
    nowFloor--;
  }
}


void goUp()
{
  mode = 0;
  moveUp();

  if (nowFloor == 2)
  {
    secondButtonStatus = 0;
    digitalWrite(BUTTON_LED_PINS[1], LOW);
  }
  if (nowFloor == 3)
  {
    thirdButtonStatus = 0;
    digitalWrite(BUTTON_LED_PINS[2], LOW);
  }
}


void goDown()
{
  mode = 1;
  moveDown();

  if (nowFloor == 2)
  {
    secondButtonStatus = 0;
    digitalWrite(BUTTON_LED_PINS[1], LOW);
  }
  if (nowFloor == 1)
  {
    firstButtonStatus = 0;
    digitalWrite(BUTTON_LED_PINS[0], LOW);
  }

}


void go()
{
  if (nowFloor == 1 
      && ( secondButtonStatus == 1 || thirdButtonStatus == 1 ))
  {
    goUp();
  }
  if (nowFloor == 2
      && thirdButtonStatus == 1)
  {
    goUp();
  }
  if (nowFloor == 2
      && firstButtonStatus == 1)
  {
    goDown();
  }
  if (nowFloor == 3
      && ( firstButtonStatus == 1 || secondButtonStatus == 1 ))
  {
    goDown();
  }
}


void stopNearestFloor()
{
  if ( lightIndex % 3 !=0 && mode == 0 )
  {
    moveUp();
  }
  if ( lightIndex % 3 !=0 && mode == 1 )
  {
    moveDown();
  }
}


void loop() {
  tellButtonStatus();
  if (called == 1)
  {
    go();
  }
  else
  {
    for (int i = 0; i < sizeof(BUTTON_LED_PINS); i++)
    {
      digitalWrite(BUTTON_LED_PINS[i], LOW);
    }
    stopNearestFloor();
  }
}