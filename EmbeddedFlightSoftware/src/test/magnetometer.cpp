// MMC5983MA 3-axis Magnetometer

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MMC56x3.h>
#include <Arduino.h>

// Create an instance of the MMC5603 magnetometer
Adafruit_MMC5603 mag = Adafruit_MMC5603();

// Define the I2C pins for the ESP32
#define I2C_SDA 21
#define I2C_SCL 22

void setup() {
  // Start serial communication for debugging
  Serial.begin(115200);
  while (!Serial) delay(10); // Wait for serial monitor to open

  Serial.println("Adafruit MMC5603 Magnetometer Test!");

  // Initialize the I2C communication
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize the magnetometer
  if (!mag.begin()) {
    Serial.println("Failed to find MMC5603 chip");
    while (1) { delay(10); }
  }
  Serial.println("MMC5603 Found!");

  // Set the sensor range and other configurations if needed
  mag.setRange(MMC5603_RANGE_16G); // Set the range to 16 Gauss (default is 16G)

  // Set output data rate (optional, default is 100Hz)
  mag.setOutputDataRate(MMC5603_ODR_100HZ);
}

void loop() {
  // Create variables to store magnetometer readings
  float x, y, z;
  
  // Read the magnetic field data in microteslas
  mag.getEvent(&x, &y, &z);

  // Print the magnetometer readings
  Serial.print("Magnetometer X: "); 
  Serial.print(x); 
  Serial.print(" uT ");
  Serial.print("Y: "); 
  Serial.print(y); 
  Serial.print(" uT ");
  Serial.print("Z: "); 
  Serial.print(z); 
  Serial.println(" uT");

  // Delay for a short period
  delay(500);
}
