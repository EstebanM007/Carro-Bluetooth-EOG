from pylsl import StreamInlet, resolve_streams  # Librería para leer streams de LSL
import time
import pandas as pd
import os  # Importar módulo para manejar rutas

# Función para buscar streams de manera continua
def buscar_stream(tipo_stream):
    while True:
        print(f"Buscando stream de tipo '{tipo_stream}'...")
        streams = [stream for stream in resolve_streams() if stream.type() == tipo_stream]
        if streams:
            print(f"Stream de tipo '{tipo_stream}' encontrado.")
            return streams[0]
        print(f"No se encontró stream de tipo '{tipo_stream}'. Reintentando en 2 segundos...")
        time.sleep(2)

# Buscar los streams de tipo 'Data1' y 'Data2'
stream_Data1 = buscar_stream('Data1')
stream_Data2 = buscar_stream('Data2')

# Crear inlets para leer datos de los streams
inlet_Data1 = StreamInlet(stream_Data1)
inlet_Data2 = StreamInlet(stream_Data2)

# Lista para almacenar los datos
data_list = []

print("Comenzando a guardar datos en 'datos_streams.xlsx'. Presiona Ctrl+C para detener.")

start_time = time.time()  # Tiempo inicial

try:
    while True:
        try:
            # Leer una muestra de cada stream
            sample_Data1, _ = inlet_Data1.pull_sample(timeout=0.5)
            sample_Data2, _ = inlet_Data2.pull_sample(timeout=0.5)

            # Verificar que ambas muestras sean válidas
            if sample_Data1 and sample_Data2:
                elapsed_time = time.time() - start_time  # Tiempo transcurrido en segundos
                # Agregar los datos a la lista
                data_list.append([elapsed_time, sample_Data1[0], sample_Data2[0]])
                # Este print verifica los datos que se están guardando, pero puede ser comentado para evitar saturar la consola.
                # print(f"Guardado: Tiempo={elapsed_time:.3f}s, Data1={sample_Data1[0]}, Data2={sample_Data2[0]}")

        except Exception as e:
            print(f"Error al leer los streams: {e}. Intentando reconectar...")
            # Intentar reconectar los streams
            stream_Data1 = buscar_stream('Data1')
            stream_Data2 = buscar_stream('Data2')
            inlet_Data1 = StreamInlet(stream_Data1)
            inlet_Data2 = StreamInlet(stream_Data2)

except KeyboardInterrupt:
    print("Detenido por el usuario. Guardando datos en 'datos_streams.csv'...")

# Crear un DataFrame con los datos
df = pd.DataFrame(data_list, columns=["Tiempo (s)", "Data1", "Data2"])

# Obtener la ruta del script actual y guardar el archivo CSV en la misma carpeta
ruta_script = os.path.dirname(os.path.abspath(__file__))  # Ruta del script actual
archivo_csv = os.path.join(ruta_script, "datos_streams.csv")  # Crear la ruta completa del archivo

# Guardar como CSV con separador ;
df.to_csv(archivo_csv, index=False, sep=';')
print(f"Archivo '{archivo_csv}' guardado correctamente.")