EXPLICACIÓN DEL PROYECTO: DETECCIÓN DE ACTIVIDAD CON ARDUINO Y PYTHON

¿QUÉ HICIMOS?

Creamos un sistema que puede reconocer lo que una persona
está haciendo (como caminar, quedarse quieta o si se cayó).
Para eso usamos un Arduino con sensores que detectan
movimientos y lo conectamos a una computadora.

Desde la compu, escribimos un programa en Python que
lee los datos que manda el Arduino. Luego, esos datos
son analizados por un modelo de machine learning
(que previamente entrenamos) para identificar la actividad.

Esto sirve mucho, por ejemplo, para detectar caídas en
personas mayores y activar una alarma en caso de emergencia.

LIBRERÍAS QUE USAMOS:

- pandas y numpy: Son librerías para manejar datos. Nos
  ayudan a trabajar con tablas y cálculos.

- serial: Nos permite leer datos del Arduino a través del
  puerto USB (COM3).

- sklearn: Se usa para crear y entrenar modelos de machine
  learning. En nuestro caso, usamos RandomForestClassifier.

- joblib: Sirve para guardar el modelo entrenado y cargarlo
  después, sin necesidad de entrenar cada vez.

- datetime: Para saber la hora exacta en que ocurre
  cada actividad.

- openpyxl: Nos permite guardar los datos en un archivo
  de Excel y crear una hoja para cada usuario.

PASOS DEL CÓDIGO:

1. Primero, el programa pide el nombre del usuario. Esto se
   usa para crear una hoja personalizada en el Excel donde
   se guardarán sus datos.

2. Luego revisa si ya existe un modelo de machine learning
   y un "scaler" (sirve para normalizar los datos). Si no
   existen, los entrena usando un archivo llamado
   "dataset_manual.csv", que tiene datos previos
   de distintas actividades.

3. Después se conecta al Arduino en el puerto COM3. 
   Una vez conectado, espera un momento para empezar
   a leer los datos.

4. Cada 7 segundos, el programa recopila muchos datos
   del sensor (aceleración y giros en 3 ejes: ax, ay, az, gx, gy, gz).

5. Esos datos se preparan y se pasan al modelo entrenado,
   que devuelve predicciones sobre qué actividad se está
   realizando (caminar, quieto, caída, etc.).

6. La actividad detectada se guarda en un archivo Excel.
   Si el usuario ya tiene una hoja, se agregan los nuevos datos.
   Si es un usuario nuevo, se crea su hoja desde cero.

7. Si el modelo detecta una caída, se manda un mensaje
   al Arduino para que active el buzzer, una especie de
   alarma sonora.

8. Si en la siguiente lectura se detecta una actividad diferente,
   el buzzer se apaga automáticamente.

ARCHIVOS IMPORTANTES:

- modelo_actividad.pkl → Aquí se guarda el modelo de machine learning entrenado.
- scaler.pkl → Este archivo guarda el "scaler" que normaliza los datos.
- dataset_manual.csv → Es el dataset manual que usamos para entrenar el modelo.
- usuarios_actividades.xlsx → Archivo Excel donde se guardan
  las actividades de cada usuario, con fecha y hora.

EXPLICACIÓN DEL CÓDIGO ARDUINO - DETECCIÓN DE CAÍDAS

1. LIBRERÍAS UTILIZADAS
------------------------
#include <Wire.h>
#include <MPU6050.h>

- Wire.h: permite la comunicación I2C entre Arduino y el MPU6050.
- MPU6050.h: facilita el uso del acelerómetro y giroscopio.

2. DECLARACIÓN DE VARIABLES
----------------------------
MPU6050 mpu;
const int buzzerPin = 8;
bool alarmaActiva = false;
unsigned long tiempoUltimaCaida = 0;
const unsigned long duracionAlarma = 5000;

- Se crea un objeto 'mpu' para manejar el sensor.
- Se define el pin para el buzzer (pin 8).
- Se usan variables para controlar el estado de la alarma y su duración.

3. FUNCIÓN setup()
------------------
- Se inicia la comunicación serial con 115200 baudios.
- Se inicia la comunicación I2C.
- Se configura el pin del buzzer como salida y se apaga.
- Se inicializa el sensor MPU6050.
- Si falla la conexión con el sensor, el programa se detiene.

4. FUNCIÓN loop()
------------------
- Se leen valores del acelerómetro (ax, ay, az) y giroscopio (gx, gy, gz).
- Los datos se envían por el puerto Serial separados por comas.
- Se revisa si hay comandos desde Python.

5. COMANDOS DESDE PYTHON
-------------------------
- "buzzer_on": activa la alarma y guarda el momento de activación.
- "buzzer_off": desactiva la alarma y apaga el buzzer.

6. ACTIVACIÓN DEL BUZZER
-------------------------
- Si la alarma está activa y no han pasado 5 segundos:
    - Se hace un barrido de frecuencias desde 100 Hz a 5000 Hz.
    - Cambia el tono cada 10 ms.
    - Se apaga el buzzer al final.
- Si ya pasaron 5 segundos desde la activación:
    - Se apaga la alarma y el buzzer.

7. RETARDO FINAL
-----------------
- Se incluye un delay de 5 ms para estabilidad.

Este sistema permite detectar caídas usando el sensor MPU6050, y activa una alarma sonora controlada desde un programa en Python.
