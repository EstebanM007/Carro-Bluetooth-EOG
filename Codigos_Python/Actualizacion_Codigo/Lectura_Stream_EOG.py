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

# Resolver streams de EOG
print("Buscando stream EOG...")
streams_EOG = [stream for stream in all_streams if stream.type() == 'EOG']

# Verificar que se haya encontrado al menos un stream de tipo 'EOG'
if len(streams_EOG) == 0:
    raise RuntimeError("No se encontró ningún stream de EOG.")

# Crear un inlet para leer datos del primer stream de tipo 'EOG'
inlet_EOG = StreamInlet(streams_EOG[0])

# Bucle principal para procesar los datos del stream
while True:
    # Leer una muestra del stream con un tiempo de espera de 0.5 segundos
    sample, _ = inlet_EOG.pull_sample(timeout=0.5)
    if sample:
        # Aplicar condiciones a la señal EOG
        if 400 <= sample[0] <= 450:
            serialPort.write(b'D')  # Enviar comando 'D' por el puerto serial
        elif -450 <= sample[0] <= -400:
            serialPort.write(b'W')  # Enviar comando 'W' por el puerto serial
