from pylsl import StreamInlet, resolve_streams  # Librería para leer streams de LSL
import serial

# Configuración del puerto serial
serialPort = serial.Serial('COM3', 9600, timeout=1)
print("Puerto serial configurado correctamente.")

# Resolver todos los streams disponibles
print("Buscando todos los streams disponibles...")
all_streams = resolve_streams()

# Mostrar los tipos de streams encontrados
print("Tipos de streams disponibles:")
for stream in all_streams:
    print(f"- {stream.name()} (Tipo: {stream.type()})")

# Resolver streams de EOG1 y EOG2
print("Buscando streams EOG1 y EOG2...")
streams_EOG1 = [stream for stream in all_streams if stream.type() == 'EOG1']
streams_EOG2 = [stream for stream in all_streams if stream.type() == 'EOG2']

# Verificar que se hayan encontrado los streams de tipo 'EOG1' y 'EOG2'
if len(streams_EOG1) == 0:
    raise RuntimeError("No se encontró ningún stream de EOG1.")
if len(streams_EOG2) == 0:
    raise RuntimeError("No se encontró ningún stream de EOG2.")

# Crear inlets para leer datos de los streams EOG1 y EOG2
inlet_EOG1 = StreamInlet(streams_EOG1[0])
inlet_EOG2 = StreamInlet(streams_EOG2[0])

# Bucle principal para procesar los datos de los streams
while True:
    # Leer una muestra de cada stream con un tiempo de espera de 0.5 segundos
    sample_EOG1, _ = inlet_EOG1.pull_sample(timeout=0.5)
    sample_EOG2, _ = inlet_EOG2.pull_sample(timeout=0.5)

    # Procesar datos de EOG1
    if sample_EOG1:
        if 400 <= sample_EOG1[0] <= 450:
            serialPort.write(b'D')  # Enviar comando 'D' por el puerto serial
        elif -450 <= sample_EOG1[0] <= -400:
            serialPort.write(b'I')  # Enviar comando 'I' por el puerto serial

    # Procesar datos de EOG2
    if sample_EOG2:
        if 300 <= sample_EOG2[0] <= 350:
            serialPort.write(b'W')  # Enviar comando 'W' por el puerto serial
        elif -350 <= sample_EOG2[0] <= -300:
            serialPort.write(b'S')  # Enviar comando 'S' por el puerto serial
