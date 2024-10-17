#include "SparkFun_I2C_GPS_Arduino_Library.h"
I2CGPS myI2CGPS; //Hook object to the library

void setup()
{
  Serial.begin(115200);
  Serial.println("GTOP Read Example");

  if (myI2CGPS.begin() == false)//Checks for succesful initialization of GPS
  {
    Serial.println("Module failed to respond. Please check wiring.");
    while (1); //Freeze!
  }
  Serial.println("GPS module found!");
}

void loop() //Writes GPS data to the Serial port with a baud rate of 115200
{
  while (myI2CGPS.available()) //available() returns the number of new bytes available from the GPS module
  {
    byte incoming = myI2CGPS.read(); //Read the latest byte from Qwiic GPS

    if(incoming == '$') Serial.println(); //Break the sentences onto new lines
    Serial.write(incoming); //Print this character
  }
}
