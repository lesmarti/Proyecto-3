#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const int buzzerPin = 8;

bool alarmaActiva = false;
unsigned long tiempoUltimaCaida = 0;
const unsigned long duracionAlarma = 5000; // 5 segundos de alarma

void setup() {
  Serial.begin(115200);
  Wire.begin();
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);

  mpu.initialize();
  if (!mpu.testConnection()) {
    while (1); // Detener si falla conexión
  }
}

void loop() {
  // Leer datos del MPU6050 y enviarlos por Serial
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.println(gz);

  // Leer comandos desde Python
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    if (comando == "buzzer_on") {
      alarmaActiva = true;
      tiempoUltimaCaida = millis(); // Reiniciar temporizador
    } else if (comando == "buzzer_off") {
      alarmaActiva = false;
      noTone(buzzerPin);
    }
  }

  // Si la alarma está activa, hacer barrido de frecuencia durante 5 segundos
  if (alarmaActiva) {
    if (millis() - tiempoUltimaCaida < duracionAlarma) {
      for (int freq = 100; freq <= 5000; freq += 50) {
        tone(buzzerPin, freq);
        delay(10);  // tiempo para cada frecuencia
      }
      noTone(buzzerPin);
    } else {
      alarmaActiva = false;
      noTone(buzzerPin);
    }
  }

  delay(5); // Pequeño delay para estabilidad
}

