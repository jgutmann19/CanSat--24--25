/*
 * This ESP32 code is created by esp32io.com
 *
 * This ESP32 code is released in the public domain
 *
 * For more detail (instruction and wiring diagram), visit https://esp32io.com/tutorials/esp32-28byj-48-stepper-motor-uln2003-driver
 */

// Include the AccelStepper Library
#include <AccelStepper.h>

// define step constant
#define FULLSTEP 4
#define STEP_PER_REVOLUTION 2048 // this value is from datasheet

// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
AccelStepper stepper(FULLSTEP, 19, 18, 17, 16); // ESP32 pin: GPIO19, GPIO18, GPIO17, GPIO16

void setup() {
  Serial.begin(9600);
  stepper.setMaxSpeed(1000.0);   // set the maximum speed
  stepper.setAcceleration(50.0); // set acceleration
  stepper.setSpeed(200);         // set initial speed
  stepper.setCurrentPosition(0); // set position
  stepper.moveTo(STEP_PER_REVOLUTION); // set target position: 64 steps <=> one revolution
}

void loop() {
  // change direction once the motor reaches target position
  if (stepper.distanceToGo() == 0)
    stepper.moveTo(-stepper.currentPosition());

  stepper.run(); // MUST be called in loop() function

  Serial.print(F("Current Position: "));
  Serial.println(stepper.currentPosition());
}
