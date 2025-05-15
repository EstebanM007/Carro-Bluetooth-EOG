import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import serial
import serial.tools.list_ports
from pylsl import StreamInlet, resolve_streams

# Clase que simula el puerto serial.  
# En modo simulado se utilizarán los visualizadores en la GUI sin imprimir en terminal.
class FakeSerial:
    def __init__(self):
        # Para depuración en terminal, descomenta la siguiente línea:
        # print("FakeSerial inicializado. No se usará puerto COM real.")
        pass

    def write(self, data):
        # Para depuración en terminal, descomenta la siguiente línea:
        # print(f"[FakeSerial] Enviado: {data.decode()}")
        pass

# Clase para cada fila de configuración para un stream.
class StreamConfigRow:
    def __init__(self, parent, available_streams, row_index):
        self.parent = parent
        self.row = row_index

        tk.Label(parent, text="Stream:").grid(row=self.row, column=0, padx=5, pady=5, sticky="w")
        self.stream_var = tk.StringVar()
        self.stream_menu = ttk.Combobox(parent, textvariable=self.stream_var,
                                        values=available_streams, state="readonly", width=40)
        self.stream_menu.grid(row=self.row, column=1, padx=5, pady=5)

        tk.Label(parent, text="Lim Inf (+):").grid(row=self.row, column=2, padx=5, pady=5, sticky="w")
        self.pos_lower = tk.Entry(parent, width=7)
        self.pos_lower.grid(row=self.row, column=3, padx=5, pady=5)

        tk.Label(parent, text="Lim Sup (+):").grid(row=self.row, column=4, padx=5, pady=5, sticky="w")
        self.pos_upper = tk.Entry(parent, width=7)
        self.pos_upper.grid(row=self.row, column=5, padx=5, pady=5)

        tk.Label(parent, text="Letra (+):").grid(row=self.row, column=6, padx=5, pady=5, sticky="w")
        self.pos_letter = tk.Entry(parent, width=5)
        self.pos_letter.grid(row=self.row, column=7, padx=5, pady=5)

        tk.Label(parent, text="Lim Inf (-):").grid(row=self.row, column=8, padx=5, pady=5, sticky="w")
        self.neg_lower = tk.Entry(parent, width=7)
        self.neg_lower.grid(row=self.row, column=9, padx=5, pady=5)

        tk.Label(parent, text="Lim Sup (-):").grid(row=self.row, column=10, padx=5, pady=5, sticky="w")
        self.neg_upper = tk.Entry(parent, width=7)
        self.neg_upper.grid(row=self.row, column=11, padx=5, pady=5)

        tk.Label(parent, text="Letra (-):").grid(row=self.row, column=12, padx=5, pady=5, sticky="w")
        self.neg_letter = tk.Entry(parent, width=5)
        self.neg_letter.grid(row=self.row, column=13, padx=5, pady=5)

    def get_data(self):
        try:
            data = {
                "stream": self.stream_var.get(),  # Ejemplo: "OpenViBE Stream (EEG)"
                "pos_lower": float(self.pos_lower.get()),
                "pos_upper": float(self.pos_upper.get()),
                "pos_letter": self.pos_letter.get(),
                "neg_lower": float(self.neg_lower.get()),
                "neg_upper": float(self.neg_upper.get()),
                "neg_letter": self.neg_letter.get(),
            }
        except ValueError:
            messagebox.showerror("Error", "Revise que los límites sean valores numéricos válidos.")
            return None
        return data

# Clase principal de la aplicación.
class App:
    def __init__(self, master):
        self.master = master
        master.title("Interfaz de Configuración LSL y COM")
        self.running = False
        self.log_viewers = {}  # Visualizadores por stream (sólo en modo simulado)

        # --- Frame de configuración del Puerto Serial ---
        self.frame_serial = tk.LabelFrame(master, text="Puerto Serial")
        self.frame_serial.pack(padx=10, pady=10, fill="x")

        tk.Label(self.frame_serial, text="Selecciona Puerto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.serial_var = tk.StringVar()
        self.serial_menu = ttk.Combobox(self.frame_serial, textvariable=self.serial_var, state="readonly", width=20)
        self.serial_menu.grid(row=0, column=1, padx=5, pady=5)
        self.btn_update_serial = tk.Button(self.frame_serial, text="Actualizar", command=self.update_serial_ports)
        self.btn_update_serial.grid(row=0, column=2, padx=5, pady=5)

        # Checkbutton para simular COM (en este modo solo se actualiza la GUI)
        self.simulate_serial = tk.BooleanVar(value=True)
        self.chk_simulate = tk.Checkbutton(
            self.frame_serial,
            text="Simular COM (mostrar en GUI)",
            variable=self.simulate_serial
        )
        self.chk_simulate.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # --- Frame de control de conexión ---
        self.frame_control = tk.Frame(master)
        self.frame_control.pack(padx=10, pady=10, fill="x")

        self.btn_connect = tk.Button(self.frame_control, text="Conectar", command=self.start_connection)
        self.btn_connect.pack(side="left", padx=5)
        self.btn_disconnect = tk.Button(self.frame_control, text="Desconectar", command=self.stop_connection, state="disabled")
        self.btn_disconnect.pack(side="left", padx=5)
        self.lbl_status = tk.Label(self.frame_control, text="Estado: Desconectado")
        self.lbl_status.pack(side="left", padx=10)

        # --- Frame de Configuración de Condiciones ---
        self.frame_conditions = tk.LabelFrame(master, text="Configuración de Condiciones")
        self.frame_conditions.pack(padx=10, pady=10, fill="both", expand=True)

        # Fila superior: botones Agregar/Quitar y selector global de streams.
        btn_frame = tk.Frame(self.frame_conditions)
        btn_frame.grid(row=0, column=0, columnspan=14, sticky="w", padx=5, pady=5)
        self.btn_add_stream = tk.Button(btn_frame, text="Agregar Stream", command=self.add_stream_row)
        self.btn_add_stream.pack(side="left", padx=5)
        self.btn_remove_stream = tk.Button(btn_frame, text="Quitar Stream", command=self.remove_stream_row)
        self.btn_remove_stream.pack(side="left", padx=5)
        tk.Label(btn_frame, text="Streams:").pack(side="left", padx=5)
        self.global_streams_var = tk.StringVar()
        self.global_streams_menu = ttk.Combobox(btn_frame, textvariable=self.global_streams_var, state="readonly", width=40)
        self.global_streams_menu.pack(side="left", padx=5)
        self.btn_update_streams = tk.Button(btn_frame, text="Actualizar", command=self.update_streams)
        self.btn_update_streams.pack(side="left", padx=5)

        # Contenedor para las filas de configuración (condiciones para cada stream).
        self.conditions_container = tk.Frame(self.frame_conditions)
        self.conditions_container.grid(row=1, column=0, columnspan=14, padx=5, pady=5)

        # --- Frame para la Visualización de Condiciones (solo en modo simulado) ---
        self.frame_logs = None

        # Variables internas para listas: puertos, streams y filas configuradas.
        self.available_serial_ports = []
        self.available_lsl_streams = []
        self.condition_rows = []
        self.update_serial_ports()
        self.update_streams()

    def update_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        self.available_serial_ports = [port.device for port in ports]
        self.serial_menu['values'] = self.available_serial_ports
        if self.available_serial_ports:
            self.serial_var.set(self.available_serial_ports[0])
        else:
            self.serial_var.set("")

    def update_streams(self):
        try:
            streams = resolve_streams()
            self.available_lsl_streams = [f"{s.name()} ({s.type()})" for s in streams]
            self.global_streams_menu['values'] = self.available_lsl_streams
            if self.available_lsl_streams:
                self.global_streams_var.set(self.available_lsl_streams[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al resolver streams: {e}")
        # Actualizar cada combobox de las filas configuradas.
        for row in self.condition_rows:
            row.stream_menu['values'] = self.available_lsl_streams

    def add_stream_row(self):
        row_index = len(self.condition_rows) + 2  # Para evitar colisiones con la fila superior.
        new_row = StreamConfigRow(self.conditions_container, self.available_lsl_streams, row_index)
        self.condition_rows.append(new_row)

    def remove_stream_row(self):
        if self.condition_rows:
            row = self.condition_rows.pop()
            for widget in self.conditions_container.grid_slaves(row=row.row):
                widget.destroy()

    def setup_log_viewers(self):
        """Crea un visualizador (Text con Scrollbar) para cada stream configurado (modo simulado)."""
        if self.frame_logs:
            self.frame_logs.destroy()
        self.frame_logs = tk.LabelFrame(self.master, text="Visualización de Condiciones (Simulación)")
        self.frame_logs.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_viewers = {}
        for stream_id in self.conditions_by_stream.keys():
            frame = tk.LabelFrame(self.frame_logs, text=f"Stream: {stream_id}")
            frame.pack(padx=5, pady=5, fill="both", expand=True)
            txt = scrolledtext.ScrolledText(frame, height=6)
            txt.pack(padx=5, pady=5, fill="both", expand=True)
            self.log_viewers[stream_id] = txt

    def update_log(self, stream_id, message):
        """Actualiza el visualizador correspondiente en la GUI.
           Se usa solo en modo simulado.
        """
        if stream_id in self.log_viewers:
            viewer = self.log_viewers[stream_id]
            viewer.insert(tk.END, message + "\n")
            viewer.see(tk.END)

    def start_connection(self):
        # Seleccionar el objeto serial según el modo.
        if self.simulate_serial.get():
            self.serial_connection = FakeSerial()
        else:
            port = self.serial_var.get()
            if not port:
                messagebox.showerror("Error", "Seleccione un puerto serial.")
                return
            try:
                self.serial_connection = serial.Serial(port, 9600, timeout=1)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar al puerto: {e}")
                return

        self.running = True
        self.lbl_status.config(text="Estado: Conectado")
        self.btn_connect.config(state="disabled")
        self.btn_disconnect.config(state="normal")

        # Recolectar la configuración de cada fila.
        self.stream_conditions = []
        for row in self.condition_rows:
            data = row.get_data()
            if data is None:
                return
            self.stream_conditions.append(data)

        # Agrupar las condiciones por stream.
        self.conditions_by_stream = {}
        for cond in self.stream_conditions:
            stream_id = cond["stream"]
            self.conditions_by_stream.setdefault(stream_id, []).append(cond)
        # Inicializar los flags de activación para cada condición (detectar el flanco de activación).
        for cond_list in self.conditions_by_stream.values():
            for cond in cond_list:
                cond["pos_triggered"] = False
                cond["neg_triggered"] = False

        # Crear inlets para cada stream configurado.
        self.inlets = {}
        for stream_id in self.conditions_by_stream.keys():
            try:
                all_streams = resolve_streams()
                match_streams = [s for s in all_streams if f"{s.name()} ({s.type()})" == stream_id]
                if not match_streams:
                    messagebox.showerror("Error", f"No se encontró el stream: {stream_id}")
                    self.stop_connection()
                    return
                self.inlets[stream_id] = StreamInlet(match_streams[0])
            except Exception as e:
                messagebox.showerror("Error", f"Error al conectar al stream {stream_id}: {e}")
                self.stop_connection()
                return

        # En modo simulado se configura el visualizador; en modo COM se elimina.
        if self.simulate_serial.get():
            self.setup_log_viewers()
        else:
            if self.frame_logs:
                self.frame_logs.destroy()
                self.frame_logs = None

        # Inicia el ciclo de lectura en un hilo separado.
        threading.Thread(target=self.lsl_connection_loop, daemon=True).start()

    def stop_connection(self):
        self.running = False
        self.lbl_status.config(text="Estado: Desconectado")
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        if not self.simulate_serial.get():
            try:
                self.serial_connection.close()
            except Exception:
                pass
        if self.frame_logs:
            self.frame_logs.destroy()
            self.frame_logs = None

    def lsl_connection_loop(self):
        """
        En cada iteración se extrae la muestra de cada inlet y se evalúan las condiciones.
        Se envía el comando correspondiente SOLO al producirse la transición (de inactivo a activo).
        Timeout reducido (0.1 s) y sleep (0.01 s) para mejorar la respuesta.
        En modo simulado se actualiza el visualizador; en modo COM real, se envía sólo el comando.
        """
        while self.running:
            for stream_id, inlet in self.inlets.items():
                sample, _ = inlet.pull_sample(timeout=0.1)
                if sample:
                    value = sample[0]
                    for cond in self.conditions_by_stream.get(stream_id, []):
                        # Evaluación de condición positiva:
                        if cond["pos_lower"] <= value <= cond["pos_upper"]:
                            if not cond["pos_triggered"]:
                                cmd = cond["pos_letter"]
                                self.serial_connection.write(cmd.encode())
                                if self.simulate_serial.get():
                                    msg = f"Valor {value:.2f} en [{cond['pos_lower']}, {cond['pos_upper']}]: enviando '{cmd}' (Positivo)"
                                    self.master.after(0, self.update_log, stream_id, msg)
                                cond["pos_triggered"] = True
                        else:
                            cond["pos_triggered"] = False

                        # Evaluación de condición negativa:
                        if cond["neg_lower"] <= value <= cond["neg_upper"]:
                            if not cond["neg_triggered"]:
                                cmd = cond["neg_letter"]
                                self.serial_connection.write(cmd.encode())
                                if self.simulate_serial.get():
                                    msg = f"Valor {value:.2f} en [{cond['neg_lower']}, {cond['neg_upper']}]: enviando '{cmd}' (Negativo)"
                                    self.master.after(0, self.update_log, stream_id, msg)
                                cond["neg_triggered"] = True
                        else:
                            cond["neg_triggered"] = False
            time.sleep(0.01)
        # Cuando se detenga, el indicador se actualizará en stop_connection().

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
