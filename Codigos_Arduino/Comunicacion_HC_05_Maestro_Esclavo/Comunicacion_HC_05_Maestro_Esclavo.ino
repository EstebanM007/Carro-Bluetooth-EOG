#include <SoftwareSerial.h>

SoftwareSerial bluetooth(10, 11); // TX,RX

void setup() {
  Serial.begin(9600); // Inicializar el monitor serial
  bluetooth.begin(9600); // Inicializar el puerto serial del HC-05
  Serial.println("Arduino Maestro iniciado. Escribe tus datos para enviar:");
}

void loop() {
  // Leer datos del monitor serial y enviarlos por Bluetooth
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    Serial.print("Enviando por Bluetooth: ");
    Serial.println(data);
    bluetooth.println(data);
  }

  // Leer datos de Bluetooth y mostrarlos en el monitor serial
  if (bluetooth.available()) {
    String receivedData = bluetooth.readStringUntil('\n');
    Serial.print("Recibido por Bluetooth: ");
    Serial.println(receivedData);
  }

  delay(500); // Ajustar el delay según sea necesario
}
