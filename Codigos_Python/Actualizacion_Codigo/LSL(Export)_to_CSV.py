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

# Buscar los streams de tipo 'P1' y 'P2'
stream_P1 = buscar_stream('P1')
stream_P2 = buscar_stream('P2')

# Crear inlets para leer datos de los streams
inlet_P1 = StreamInlet(stream_P1)
inlet_P2 = StreamInlet(stream_P2)

# Lista para almacenar los datos
data_list = []

print("Comenzando a guardar datos en 'datos_streams.xlsx'. Presiona Ctrl+C para detener.")

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
                # Agregar los datos a la lista
                data_list.append([elapsed_time, sample_P1[0], sample_P2[0]])
                # Este print verifica los datos que se están guardando, pero puede ser comentado para evitar saturar la consola.
                # print(f"Guardado: Tiempo={elapsed_time:.3f}s, P1={sample_P1[0]}, P2={sample_P2[0]}")

        except Exception as e:
            print(f"Error al leer los streams: {e}. Intentando reconectar...")
            # Intentar reconectar los streams
            stream_P1 = buscar_stream('P1')
            stream_P2 = buscar_stream('P2')
            inlet_P1 = StreamInlet(stream_P1)
            inlet_P2 = StreamInlet(stream_P2)

except KeyboardInterrupt:
    print("Detenido por el usuario. Guardando datos en 'datos_streams.xlsx'...")

# Crear un DataFrame con los datos
df = pd.DataFrame(data_list, columns=["Tiempo (s)", "P1", "P2"])

# Obtener la ruta del script actual y guardar el archivo Excel en la misma carpeta
ruta_script = os.path.dirname(os.path.abspath(__file__))  # Ruta del script actual
archivo_excel = os.path.join(ruta_script, "datos_streams.xlsx")  # Crear la ruta completa del archivo
df.to_excel(archivo_excel, index=False)
print(f"Archivo '{archivo_excel}' guardado correctamente.")