// GY-291 ADXL345 Digital 3-Axis Acceleration of Gravity Tilt Module IIC/SPI
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

// Create an instance of the ADXL345
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified();

void setup() {
  Serial.begin(9600);
  // Initialize I2C communication
  Wire.begin();

  // Initialize the ADXL345
  if (!accel.begin()) {
    Serial.println("No ADXL345 detected, check your connections!");
    while (1); // Halt
  }

  // Set the range to +/- 16g
  accel.setRange(ADXL345_RANGE_16_G);
  // Set the data rate to 100 Hz
  accel.setDataRate(ADXL345_DATARATE_100_HZ);
  
  Serial.println("ADXL345 initialized.");
}

void loop() {
  sensors_event_t event; 
  accel.getEvent(&event);
  
  // Print the acceleration values
  Serial.print("X: "); Serial.print(event.acceleration.x); Serial.print(" m/s^2");
  Serial.print("\tY: "); Serial.print(event.acceleration.y); Serial.print(" m/s^2");
  Serial.print("\tZ: "); Serial.print(event.acceleration.z); Serial.print(" m/s^2");
  Serial.println();

  delay(500); // Delay for readability
}