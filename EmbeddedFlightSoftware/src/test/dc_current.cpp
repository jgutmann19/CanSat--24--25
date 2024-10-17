//Library Reference: https://learn.adafruit.com/adafruit-ina219-current-sensor-breakout/library-reference

#include <Wire.h>
#include <Adafruit_INA219.h>

//Constructs an instance of the Adafruit_INA219.  If no address is specified, the default address (0x40) is used.
Adafruit_INA219 ina219_A;

void setup(void) 
{
  ina219_A.begin();  // Initialize first board (default address 0x40)
}

void loop(void)
{
    float shuntvoltage = ina219.getShuntVoltage_mV();
    float busvoltage = ina219.getBusVoltage_V();
    float current_mA = ina219.getCurrent_mA();
    float loadvoltage = busvoltage + (shuntvoltage / 1000);
    
    Serial.print("Bus Voltage:   "); Serial.print(busvoltage); Serial.println(" V");
    Serial.print("Shunt Voltage: "); Serial.print(shuntvoltage); Serial.println(" mV");
    Serial.print("Load Voltage:  "); Serial.print(loadvoltage); Serial.println(" V");
    Serial.print("Current:       "); Serial.print(current_mA); Serial.println(" mA");
    Serial.println("");
}