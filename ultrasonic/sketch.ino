#include <ESP32Servo.h>
Servo servo;

#define servoPin 26
#define irPin 25
#define TRIG_PIN 14
#define ECHO_PIN 34
int green = 32;
int red = 33;
int yellow = 13;

long echoDuration;
float distanceCm;

void setup() {
  Serial.begin(9600);
  servo.attach(servoPin);

  pinMode(irPin, INPUT);
  pinMode(green, OUTPUT);
  pinMode(red, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {


  if(digitalRead(irPin) == HIGH ) {
    servo.write(0);
    digitalWrite(red, LOW);
    digitalWrite(green, HIGH);
    delay(1000);
  }
  
  if(digitalRead(irPin) == LOW && distanceCm > 5.00) {
    servo.write(180);
    digitalWrite(red, HIGH);
    digitalWrite(green, LOW);
    delay(1500);
  }




// Clears the trigPin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
 
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  echoDuration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate the distance in Centimeter
  distanceCm = echoDuration * 0.034 / 2;

  Serial.println(distanceCm); 
}


