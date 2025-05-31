import pandas as pd
import numpy as np
import serial
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime

# === CONFIGURACIÓN ===
puerto_serial = 'COM3'
baudrate = 115200
tiempo_lectura = 7
archivo_modelo = 'modelo_actividad.pkl'
archivo_scaler = 'scaler.pkl'
archivo_excel = "usuarios_actividades.xlsx"

# === INGRESO DE USUARIO ===
usuario = input("👤 Ingresa tu nombre de usuario: ").strip()

# === ENTRENAR O CARGAR MODELO Y SCALER ===
if os.path.exists(archivo_modelo) and os.path.exists(archivo_scaler):
    print("📂 Cargando modelo y scaler desde archivos existentes...")
    modelo = joblib.load(archivo_modelo)
    scaler = joblib.load(archivo_scaler)
else:
    print("🛠️ Entrenando modelo desde dataset_manual.csv...")
    df = pd.read_csv('dataset_manual.csv')

    print("\n📊 Recuento de clases en el dataset:")
    print(df['label'].value_counts())

    X = df[['ax', 'ay', 'az', 'gx', 'gy', 'gz']]
    y = df['label']

    scaler = StandardScaler()
    X_normalizado = scaler.fit_transform(X)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_normalizado, y)

    joblib.dump(modelo, archivo_modelo)
    joblib.dump(scaler, archivo_scaler)
    print("✅ Modelo y scaler guardados.")

# === CONECTAR CON ARDUINO ===
try:
    ser = serial.Serial(puerto_serial, baudrate, timeout=1)
    print(f"✅ Conectado a {puerto_serial}")
    time.sleep(2)
except Exception as e:
    print(f"❌ No se pudo conectar al puerto: {e}")
    exit()

print("\n🎯 Iniciando reconocimiento continuo de actividad cada 7 segundos.\nPresiona Ctrl+C para salir.\n")

buzzer_encendido = False

try:
    while True:
        datos_reales = []
        start_time = time.time()
        print("⏳ Capturando datos...")

        while time.time() - start_time < tiempo_lectura:
            try:
                linea = ser.readline().decode('utf-8').strip()
                valores = list(map(int, linea.split(',')))
                if len(valores) == 6:
                    datos_reales.append(valores)
            except Exception:
                continue

        if not datos_reales:
            print("⚠️ No se recibieron datos.\n")
            continue

        df_reales = pd.DataFrame(datos_reales, columns=['ax', 'ay', 'az', 'gx', 'gy', 'gz'])

        print("📊 Muestra de datos capturados:")
        print(df_reales.head())

        X_reales = scaler.transform(df_reales)
        predicciones = modelo.predict(X_reales)

        print("🔍 Predicciones individuales:", predicciones)

        actividad_predicha = pd.Series(predicciones).mode()[0]
        print(f"🤖 Actividad detectada: {actividad_predicha.upper()}\n")

        # === GUARDAR EN ARCHIVO EXCEL (HOJA POR USUARIO) ===
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        nuevo_registro = pd.DataFrame([[fecha_actual, actividad_predicha]], columns=["fecha", "actividad"])

        # Cargar archivo si existe
        if os.path.exists(archivo_excel):
            with pd.ExcelWriter(archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                try:
                    hoja_actual = pd.read_excel(archivo_excel, sheet_name=usuario)
                    hoja_actual = pd.concat([hoja_actual, nuevo_registro], ignore_index=True)
                except:
                    hoja_actual = nuevo_registro

                hoja_actual.to_excel(writer, sheet_name=usuario, index=False)
        else:
            with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
                nuevo_registro.to_excel(writer, sheet_name=usuario, index=False)

        # === BUZZER ===
        if actividad_predicha.lower() == "caída":
            print("⚠️ ¡CAÍDA DETECTADA! Activando buzzer...")
            ser.write(b"buzzer_on\n")
            buzzer_encendido = True
        else:
            if buzzer_encendido:
                print("✅ Actividad diferente detectada. Apagando buzzer...")
                ser.write(b"buzzer_off\n")
                buzzer_encendido = False

except KeyboardInterrupt:
    print("🛑 Reconocimiento detenido por el usuario.")
    ser.close()
