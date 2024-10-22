// HiLetgo PCT2075 Temperature Sensor

#include <Wire.h>
#include <Arduino.h>

//need to include ^wire.h file. doesn't give errors without it??
#define PCT2075_ADDRESS 0x48  // Default I2C address for PCT2075

void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(1000); //for sensor to stabilize 
  Serial.println("PCT2075 Temperature Sensor Initialization");
}

void loop() {
    //reading temperature
  Wire.beginTransmission(PCT2075_ADDRESS);
  Wire.write(0x00);
  Wire.endTransmission(); 
  Wire.requestFrom(PCT2075_ADDRESS, 2);
  if(Wire.available() = 2 )
  float temperature = readTemperature();
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

}