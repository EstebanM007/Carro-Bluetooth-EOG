#include <SoftwareSerial.h>

// Definición de pines para el TB6612FNG
#define PWM1 3
#define AIN2 4
#define AIN1 5
#define STBY 6
#define BIN1 7
#define BIN2 8
#define PWM2 9


SoftwareSerial BTSerial(10, 11); // TX 10, RX 11
char estado = 'C'; // Estado inicial en reposo
int Vel1 = 80;
int Vel2 = 80;

unsigned long startTime = 0;
bool enMovimiento = false;

void setup() {
  Serial.begin(9600);
  BTSerial.begin(9600);

  pinMode(PWM1, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWM2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(STBY, OUTPUT);
  digitalWrite(STBY, HIGH); // Activa el driver

  Serial.println("Arduino Receptor iniciado. Esperando comandos...");
}

void loop() {
  // Leer datos del monitor serial y de Bluetooth
  if (BTSerial.available() > 0) {
    estado = BTSerial.read();
    Serial.print("Caracter recibido por Bluetooth: ");
    Serial.println(estado);

    // Iniciar temporizador y activar el movimiento cuando se recibe un comando
    startTime = millis();
    enMovimiento = true;
  }

  if (Serial.available() > 0) {
    estado = Serial.read();
    Serial.print("Caracter recibido por monitor serial: ");
    Serial.println(estado);

    // Iniciar temporizador y activar el movimiento cuando se recibe un comando
    startTime = millis();
    enMovimiento = true;
  }
  // Ejecutar acciones basadas en el comando recibido si el temporizador está activo
  if (enMovimiento) {
    switch (estado) {
      case 'W': // Mover hacia adelante
        digitalWrite(AIN1, HIGH);
        digitalWrite(AIN2, LOW);
        analogWrite(PWM1, Vel1);

        digitalWrite(BIN1, LOW);
        digitalWrite(BIN2, HIGH);
        analogWrite(PWM2, Vel2);
        //BTSerial.println("Moviendo hacia adelante");
        break;

      case 'S': // Mover hacia atrás
        digitalWrite(AIN1, LOW);
        digitalWrite(AIN2, HIGH);
        analogWrite(PWM1, Vel1);

        digitalWrite(BIN1, HIGH);
        digitalWrite(BIN2, LOW);
        analogWrite(PWM2, Vel2);
        //BTSerial.println("Moviendo hacia atrás");
        break;

      case 'A': // Girar a la izquierda
        digitalWrite(AIN1, LOW);
        digitalWrite(AIN2, HIGH);
        analogWrite(PWM1, Vel1);

        digitalWrite(BIN1, LOW);
        digitalWrite(BIN2, HIGH);
        analogWrite(PWM2, Vel2);
        //BTSerial.println("Girando a la izquierda");
        break;

      case 'D': // Girar a la derecha
        digitalWrite(AIN1, HIGH);
        digitalWrite(AIN2, LOW);
        analogWrite(PWM1, Vel1);

        digitalWrite(BIN1, HIGH);
        digitalWrite(BIN2, LOW);
        analogWrite(PWM2, Vel2);
        //BTSerial.println("Girando a la derecha");
        break;
    }
    
    // Verificar si han pasado 3 segundos desde el inicio del movimiento
    if (millis() - startTime >= 330) {
      // Detener los motores y resetear el estado
      analogWrite(PWM1, 0);
      analogWrite(PWM2, 0);
      enMovimiento = false;
      estado = 'C';  // Estado de reposo
      //BTSerial.println("Tiempo cumplido, motores detenidos");
    }
  }
  else {
    // Parar los motores si no se recibe un comando válido o ha expirado el tiempo
    analogWrite(PWM1, 0);
    analogWrite(PWM2, 0);
  }
}
