#include "ArduinoJson.h"
/* Encode 1000 packets with a fixed data set
   and send across the serial link
*/

StaticJsonDocument<159> doc;
char output[159];
size_t length;

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
  //size_t length = serializeMsgPack(doc, output);
  //Serial.write(length);
  //for(int i = 0; i < length; i++){
  //  Serial.write(output[i]);
  //}

  // give some time to start the python deserializer
  delay(5000);

}

void loop() {
  length = serializeMsgPack(doc, output);
  Serial.write(length);
  for (int i = 0; i < length; i++) {
    Serial.write(output[i]);
  }
  // bump the counter and adjust the value in the document
  counter += 1;
  doc["count"] = counter;

}