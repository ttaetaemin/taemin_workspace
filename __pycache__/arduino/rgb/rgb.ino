const int R_LED = 3;
const int G_LED = 5;
const int B_LED = 6;

unsigned long previousMillis = 0;
const unsigned long interval = 1000;

int colorIndex = 0;

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);

  pinMode(R_LED, OUTPUT);
  pinMode(G_LED, OUTPUT);
  pinMode(B_LED, OUTPUT);

}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;  

    switch (colorIndex) {
      case 0:  // Blue
        digitalWrite(R_LED, HIGH);
        digitalWrite(G_LED, LOW);
        digitalWrite(B_LED, LOW);
        break;
      case 1:  // Green
        digitalWrite(R_LED, LOW);
        digitalWrite(G_LED, HIGH);
        digitalWrite(B_LED, LOW);
        break;
      case 2:  // Red
        digitalWrite(R_LED, LOW);
        digitalWrite(G_LED, LOW);
        digitalWrite(B_LED, HIGH);
        break;
    }

    colorIndex = (colorIndex + 1) % 3;
  }
}



  // while (Serial.available() > 0)
  // {
  //   Serial.println("----");
  //   char input = Serial.read();
  //   Serial.println(input);

  //   if (input == 'r') // blue
  //   {
  //     digitalWrite(R_LED, HIGH);
  //     digitalWrite(G_LED, LOW);
  //     digitalWrite(B_LED, LOW);      
  //   }

  //   else if (input == 'g') // grin
  //   {
  //     digitalWrite(R_LED, LOW);
  //     digitalWrite(G_LED, HIGH);
  //     digitalWrite(B_LED, LOW);     
  //   }
  //   else if (input == 'b') // red
  //   {
  //     digitalWrite(R_LED, LOW);
  //     digitalWrite(G_LED, LOW);
  //     digitalWrite(B_LED, HIGH);     
  //   } 
    
  //   else 
  //   {
  //     Serial.println("Not a command !!");
  //   }
  // }
  // for(int i = 0; i < 255; i++) {
  //   analogWrite(R_LED, i);
  //   analogWrite(G_LED, i);
  //   analogWrite(B_LED, i);
  //   delay(10);  
  // }
// }
