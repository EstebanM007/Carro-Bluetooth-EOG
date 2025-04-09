from pylsl import StreamInlet, resolve_streams  # Librería para leer streams de LSL
import csv
import time

# Resolver todos los streams disponibles
print("Buscando todos los streams disponibles...")
all_streams = resolve_streams()

# Filtrar los streams de tipo 'P1' y 'P2'
stream_P1 = next((stream for stream in all_streams if stream.type() == 'P1'), None)
stream_P2 = next((stream for stream in all_streams if stream.type() == 'P2'), None)

# Verificar que ambos streams estén disponibles
if not stream_P1 or not stream_P2:
    raise RuntimeError("No se encontraron ambos streams de tipo 'P1' y 'P2'.")

# Crear inlets para leer datos de los streams
inlet_P1 = StreamInlet(stream_P1)
inlet_P2 = StreamInlet(stream_P2)

# Crear un archivo CSV para guardar los datos
with open("datos_streams.csv", mode="w", newline="") as file:
    writer = csv.writer(file, delimiter=',')  # Asegurarse de usar coma como delimitador
    # Escribir encabezados
    writer.writerow(["Tiempo (s)", "P1", "P2"])

    print("Comenzando a guardar datos en 'datos_streams.csv'. Presiona Ctrl+C para detener.")

    start_time = time.time()  # Tiempo inicial

    try:
        while True:
            try:
                # Leer una muestra de cada stream
                sample_P1, _ = inlet_P1.pull_sample(timeout=0.5)
                sample_P2, _ = inlet_P2.pull_sample(timeout=0.5)

                # Verificar que ambas muestras sean válidas
                if sample_P1 and sample_P2:
                    elapsed_time = time.time() - start_time  # Tiempo transcurrido en segundos
                    # Guardar los datos en el archivo CSV
                    writer.writerow([elapsed_time, sample_P1[0], sample_P2[0]])
                    print(f"Guardado: Tiempo={elapsed_time:.3f}s, P1={sample_P1[0]}, P2={sample_P2[0]}")

            except Exception as e:
                print(f"Error al leer los streams: {e}. Intentando reconectar...")
                # Intentar reconectar los streams
                inlet_P1 = StreamInlet(stream_P1)
                inlet_P2 = StreamInlet(stream_P2)

    except KeyboardInterrupt:
        print("Detenido por el usuario. Archivo guardado como 'datos_streams.csv'.")