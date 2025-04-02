from pylsl import StreamInlet, resolve_stream
import keyboard
import time
import serial

# Configuración del puerto serial
serialPort = serial.Serial('COM10', 9600, timeout=1)
print("Puerto serial configurado correctamente.")

# Resolver streams de EOG
print("Buscando stream EOG...")
streams_EOG = resolve_stream('type', 'EOG')

# Verificar que se hayan encontrado ambos streams
if len(streams_EOG) == 0:
    raise RuntimeError("No se encontró ningún stream de EOG.")

# Crear inlets para leer de cada stream
inlet_EOG = StreamInlet(streams_EOG[0], max_buflen=5)

sample_block_size = 16  # Bloques de 16 muestras

while True:
    if keyboard.is_pressed('q'):
        print("Programa terminado por el usuario.")
        break

    # Leer datos de EOG
    chunk_EOG, _ = inlet_EOG.pull_chunk(timeout=0.5, max_samples=sample_block_size)
    if chunk_EOG:
        for sample_value in chunk_EOG:
            # Aplicar condiciones a la señal EOG
            if 400 <= sample_value[0] <= 450:
                serialPort.write(b'D')
            elif -450 <= sample_value[0] <= -400:
                serialPort.write(b'W')


   

    time.sleep(0.01)
