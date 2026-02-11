/*
 * VL53L5CX_Satel ToF Sensor
 *
 * Reads 8x8 distance data from VL53L5CX,
 * outputs JSON over serial.
 *
 * Wiring (both sensors share I2C bus):
 *   VIN -> 3V3
 *   GND -> GND
 *   SDA -> GPIO 21
 *   SCL -> GPIO 22
 *   LPn -> GPIO 19 (VL53L5CX enable, set HIGH)
 */

#include <Wire.h>
#include <SparkFun_VL53L5CX_Library.h>


// Version - must match viewer config.VERSION
#define VERSION "0.1.0"

// Pin definitions
#define SDA_PIN 21
#define SCL_PIN 22
#define LPN_PIN 19

// VL53L5CX ToF sensor instance
SparkFun_VL53L5CX sensor;
VL53L5CX_ResultsData measurementData;




// I2C speed - use 1MHz for fast data transfer
#define I2C_SPEED 1000000

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("{\"status\":\"initializing\"}");

  // Enable I2C on sensor by setting LPn HIGH
  pinMode(LPN_PIN, OUTPUT);
  digitalWrite(LPN_PIN, HIGH);
  delay(10);

  // Initialize I2C with specified pins and speed
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(I2C_SPEED);

  Serial.println("{\"status\":\"i2c_ready\"}");

  // Initialize sensor
  if (!sensor.begin()) {
    Serial.println("{\"error\":\"sensor_init_failed\"}");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("{\"status\":\"sensor_found\"}");

  // Configure sensor for 8x8 resolution
  sensor.setResolution(64);  // 64 zones = 8x8

  // Set ranging frequency to 15Hz (stable for continuous streaming)
  sensor.setRangingFrequency(15);

  // Start ranging
  sensor.startRanging();

  Serial.println("{\"status\":\"ranging_started\",\"resolution\":\"8x8\",\"frequency_hz\":15}");



  
}

void loop() {
  
  // Check if new ToF data is available
  if (sensor.isDataReady()) {
    if (sensor.getRangingData(&measurementData)) {
      // Output JSON with distance and quaternion data
      Serial.print("{\"distances\":[");

      for (int i = 0; i < 64; i++) {
        // Distance in mm
        Serial.print(measurementData.distance_mm[i]);
        if (i < 63) Serial.print(",");
      }

      Serial.print("],\"status\":[");

      for (int i = 0; i < 64; i++) {
        // Target status (5 = valid, others = various error states)
        Serial.print(measurementData.target_status[i]);
        if (i < 63) Serial.print(",");
      }
      Serial.print("]");
      Serial.println("}");
      
    }
  }

  // Small delay to prevent overwhelming the serial buffer
  delay(1);
}