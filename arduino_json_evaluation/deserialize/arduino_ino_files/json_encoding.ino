#include "ArduinoJson.h"
/* Encode 1000 packets with a fixed data set
   and send across the serial link

   Output of memory usage:

   Sketch uses 5478 bytes (16%) of program storage space. Maximum is 32256 bytes.
   Global variables use 514 bytes (25%) of dynamic memory, leaving 1534 bytes for local variables. Maximum is 2048 bytes.
*/

StaticJsonDocument<159> doc;

// number of packets to send
int counter = 0;


void setup() {

  Serial.begin(115200);

  doc["count"] = 0;
  doc["type"] = "r";
  doc["device"] = "i2c";
  doc["address"] = 83;
  doc["register"] = 232;
  doc["big_data"] = 2048;

  JsonArray data = doc.createNestedArray("data");
  data.add(1);
  data.add(2);
  data.add(3);
  data.add(4);
  data.add(5);
  data.add(6);

  // give some time to start the python deserializer
  delay(5000);

}

void loop() {
  // put your main code here, to run repeatedly:

  // send the serialized data
  serializeJson(doc, Serial);

  // bump the counter and adjust the value in the document
  counter += 1;
  doc["count"] = counter;

}