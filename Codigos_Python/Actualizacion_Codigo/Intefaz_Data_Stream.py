import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import serial
import serial.tools.list_ports
from pylsl import StreamInlet, resolve_streams
import json

# Clase que simula el puerto serial.
class FakeSerial:
    def write(self, data):
        pass
    def close(self):
        pass

# Clase para cada fila de configuración para un stream.
class StreamConfigRow:
    def __init__(self, parent, available_streams, row_index):
        self.parent = parent
        self.row = row_index

        tk.Label(parent, text="Stream:").grid(row=self.row, column=0, padx=5, pady=5, sticky="w")
        self.stream_var = tk.StringVar()
        self.stream_menu = ttk.Combobox(parent, textvariable=self.stream_var,
                                        values=available_streams, state="readonly", width=30)
        self.stream_menu.grid(row=self.row, column=1, padx=5, pady=5)

        tk.Label(parent, text="Lim Inf (+):").grid(row=self.row, column=2, padx=2, pady=5, sticky="w")
        self.pos_lower = tk.Entry(parent, width=7)
        self.pos_lower.grid(row=self.row, column=3, padx=2, pady=5)

        tk.Label(parent, text="Lim Sup (+):").grid(row=self.row, column=4, padx=2, pady=5, sticky="w")
        self.pos_upper = tk.Entry(parent, width=7)
        self.pos_upper.grid(row=self.row, column=5, padx=2, pady=5)

        tk.Label(parent, text="Letra (+):").grid(row=self.row, column=6, padx=2, pady=5, sticky="w")
        self.pos_letter = tk.Entry(parent, width=5)
        self.pos_letter.grid(row=self.row, column=7, padx=2, pady=5)

        tk.Label(parent, text="Lim Inf (-):").grid(row=self.row, column=8, padx=2, pady=5, sticky="w")
        self.neg_lower = tk.Entry(parent, width=7)
        self.neg_lower.grid(row=self.row, column=9, padx=2, pady=5)

        tk.Label(parent, text="Lim Sup (-):").grid(row=self.row, column=10, padx=2, pady=5, sticky="w")
        self.neg_upper = tk.Entry(parent, width=7)
        self.neg_upper.grid(row=self.row, column=11, padx=2, pady=5)

        tk.Label(parent, text="Letra (-):").grid(row=self.row, column=12, padx=2, pady=5, sticky="w")
        self.neg_letter = tk.Entry(parent, width=5)
        self.neg_letter.grid(row=self.row, column=13, padx=2, pady=5)

    def get_data(self):
        def parse_float(entry):
            val = entry.get().strip()
            return float(val) if val else None

        data = {
            "stream": self.stream_var.get(),
            "pos_lower": parse_float(self.pos_lower),
            "pos_upper": parse_float(self.pos_upper),
            "pos_letter": self.pos_letter.get().strip(),
            "neg_lower": parse_float(self.neg_lower),
            "neg_upper": parse_float(self.neg_upper),
            "neg_letter": self.neg_letter.get().strip(),
        }
        if not data["stream"]:
            messagebox.showerror("Error", "Seleccione un stream para cada fila.")
            return None
        if not (data["pos_upper"] is not None or data["neg_upper"] is not None):
            messagebox.showerror("Error", "Debe definir al menos un límite superior para cada fila.")
            return None
        if data["pos_upper"] is not None and (not data["pos_letter"] or len(data["pos_letter"]) != 1):
            messagebox.showerror("Error", "Debe definir una sola letra (+) si usa límites positivos.")
            return None
        if data["neg_upper"] is not None and (not data["neg_letter"] or len(data["neg_letter"]) != 1):
            messagebox.showerror("Error", "Debe definir una sola letra (-) si usa límites negativos.")
            return None
        return data

    def set_data(self, data):
        self.stream_var.set(data.get("stream", ""))
        self.pos_lower.delete(0, tk.END)
        self.pos_lower.insert(0, "" if data.get("pos_lower") is None else str(data.get("pos_lower")))
        self.pos_upper.delete(0, tk.END)
        self.pos_upper.insert(0, "" if data.get("pos_upper") is None else str(data.get("pos_upper")))
        self.pos_letter.delete(0, tk.END)
        self.pos_letter.insert(0, data.get("pos_letter", ""))
        self.neg_lower.delete(0, tk.END)
        self.neg_lower.insert(0, "" if data.get("neg_lower") is None else str(data.get("neg_lower")))
        self.neg_upper.delete(0, tk.END)
        self.neg_upper.insert(0, "" if data.get("neg_upper") is None else str(data.get("neg_upper")))
        self.neg_letter.delete(0, tk.END)
        self.neg_letter.insert(0, data.get("neg_letter", ""))

class App:
    def __init__(self, master):
        self.master = master
        master.title("Interfaz de Configuración LSL y COM")
        self.running = False
        self.log_viewers = {}
        self.lsl_thread = None
        self.last_samples = {}  # Para autoajuste de umbrales

        # --- Frame de configuración del Puerto Serial ---
        self.frame_serial = tk.LabelFrame(master, text="Puerto Serial")
        self.frame_serial.pack(padx=10, pady=10, fill="x")

        tk.Label(self.frame_serial, text="Selecciona Puerto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.serial_var = tk.StringVar()
        self.serial_menu = ttk.Combobox(self.frame_serial, textvariable=self.serial_var, state="readonly", width=20)
        self.serial_menu.grid(row=0, column=1, padx=5, pady=5)

        self.btn_refresh_all = tk.Button(self.frame_serial, text="Actualizar Puertos", command=self.refresh_all)
        self.btn_refresh_all.grid(row=0, column=2, padx=5, pady=5)

        self.simulate_serial = tk.BooleanVar(value=True)
        self.chk_simulate = tk.Checkbutton(
            self.frame_serial,
            text="Simular COM (mostrar en GUI)",
            variable=self.simulate_serial
        )
        self.chk_simulate.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        self.show_serial_console = tk.BooleanVar(value=True)
        self.chk_show_console = tk.Checkbutton(
            self.frame_serial,
            text="Mostrar consola serial",
            variable=self.show_serial_console,
            command=self.toggle_serial_console
        )
        self.chk_show_console.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        self.serial_console_frame = tk.LabelFrame(self.frame_serial, text="Consola Serial")
        self.serial_console_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=0, sticky="we")
        self.serial_console = scrolledtext.ScrolledText(self.serial_console_frame, height=6, state="disabled")
        self.serial_console.pack(fill="x", padx=5, pady=5)

        self.btn_clear_console = tk.Button(self.frame_serial, text="Limpiar consola", command=self.clear_console)
        self.btn_clear_console.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        # --- Frame de control de conexión y configuración ---
        self.frame_control = tk.Frame(master)
        self.frame_control.pack(padx=10, pady=10, fill="x")

        self.btn_connect = tk.Button(self.frame_control, text="Conectar", command=self.start_connection)
        self.btn_connect.pack(side="left", padx=5)
        self.btn_disconnect = tk.Button(self.frame_control, text="Desconectar", command=self.stop_connection, state="disabled")
        self.btn_disconnect.pack(side="left", padx=5)
        self.lbl_status = tk.Label(self.frame_control, text="Estado: Desconectado")
        self.lbl_status.pack(side="left", padx=10)

        self.btn_save = tk.Button(self.frame_control, text="Guardar configuración", command=self.save_config)
        self.btn_save.pack(side="left", padx=5)
        self.btn_load = tk.Button(self.frame_control, text="Cargar configuración", command=self.load_config)
        self.btn_load.pack(side="left", padx=5)
        self.btn_auto = tk.Button(self.frame_control, text="Sugerir umbrales", command=self.auto_threshold)
        self.btn_auto.pack(side="left", padx=5)

        # --- Frame de Configuración de Condiciones ---
        self.frame_conditions = tk.LabelFrame(master, text="Configuración de Condiciones")
        self.frame_conditions.pack(padx=10, pady=10, fill="both", expand=True)

        btn_frame = tk.Frame(self.frame_conditions)
        btn_frame.grid(row=0, column=0, columnspan=14, sticky="w", padx=5, pady=5)
        self.btn_add_stream = tk.Button(btn_frame, text="Agregar Stream", command=self.add_stream_row)
        self.btn_add_stream.pack(side="left", padx=5)
        self.btn_remove_stream = tk.Button(btn_frame, text="Quitar Stream", command=self.remove_stream_row)
        self.btn_remove_stream.pack(side="left", padx=5)
        tk.Label(btn_frame, text="Streams:").pack(side="left", padx=5)
        self.global_streams_var = tk.StringVar()
        self.global_streams_menu = ttk.Combobox(btn_frame, textvariable=self.global_streams_var, state="readonly", width=30)
        self.global_streams_menu.pack(side="left", padx=5)

        self.conditions_container = tk.Frame(self.frame_conditions)
        self.conditions_container.grid(row=1, column=0, columnspan=14, padx=5, pady=5)

        self.frame_logs = None
        self.available_serial_ports = []
        self.available_lsl_streams = []
        self.condition_rows = []
        self.refresh_all()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def refresh_all(self):
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
            self.master.after(0, messagebox.showerror, "Error", f"Error al resolver streams: {e}")
        for row in self.condition_rows:
            row.stream_menu['values'] = self.available_lsl_streams

    def add_stream_row(self):
        row_index = len(self.condition_rows) + 2
        new_row = StreamConfigRow(self.conditions_container, self.available_lsl_streams, row_index)
        self.condition_rows.append(new_row)

    def remove_stream_row(self):
        if self.condition_rows:
            row = self.condition_rows.pop()
            for widget in self.conditions_container.grid_slaves(row=row.row):
                widget.destroy()

    def setup_log_viewers(self):
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
        if stream_id in self.log_viewers:
            viewer = self.log_viewers[stream_id]
            viewer.insert(tk.END, message + "\n")
            viewer.see(tk.END)

    def clear_console(self):
        self.serial_console.config(state="normal")
        self.serial_console.delete(1.0, tk.END)
        self.serial_console.config(state="disabled")

    def save_config(self):
        config = [row.get_data() for row in self.condition_rows if row.get_data() is not None]
        if not config:
            messagebox.showinfo("Guardar configuración", "No hay configuración válida para guardar.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Guardar configuración", "Configuración guardada correctamente.")

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                config = json.load(f)
            # Limpiar filas actuales
            for row in self.condition_rows:
                for widget in self.conditions_container.grid_slaves(row=row.row):
                    widget.destroy()
            self.condition_rows.clear()
            # Agregar filas desde el archivo
            for i, cond in enumerate(config):
                new_row = StreamConfigRow(self.conditions_container, self.available_lsl_streams, i+2)
                new_row.set_data(cond)
                self.condition_rows.append(new_row)
            messagebox.showinfo("Cargar configuración", "Configuración cargada correctamente.")

    def auto_threshold(self):
        # Sugerir umbrales a partir de los últimos valores recibidos
        if not self.last_samples:
            messagebox.showinfo("Sugerir umbrales", "No hay datos recientes para sugerir umbrales.")
            return
        for i, row in enumerate(self.condition_rows):
            stream = row.stream_var.get()
            if stream in self.last_samples and self.last_samples[stream]:
                values = self.last_samples[stream]
                vmax = max(values)
                vmin = min(values)
                # Sugerencia: 80% del máximo/mínimo como umbral
                row.pos_upper.delete(0, tk.END)
                row.pos_upper.insert(0, f"{vmax*0.8:.2f}")
                row.pos_lower.delete(0, tk.END)
                row.pos_lower.insert(0, f"{vmax*0.2:.2f}")
                row.neg_upper.delete(0, tk.END)
                row.neg_upper.insert(0, f"{vmin*0.8:.2f}")
                row.neg_lower.delete(0, tk.END)
                row.neg_lower.insert(0, f"{vmin*0.2:.2f}")
        messagebox.showinfo("Sugerir umbrales", "Umbrales sugeridos a partir de los últimos datos.")

    def start_connection(self):
        self.btn_connect.config(state="disabled")
        self.btn_add_stream.config(state="disabled")
        self.btn_remove_stream.config(state="disabled")
        self.btn_refresh_all.config(state="disabled")
        self.serial_menu.config(state="disabled")
        self.global_streams_menu.config(state="disabled")
        for row in self.condition_rows:
            row.stream_menu.config(state="disabled")
            row.pos_lower.config(state="disabled")
            row.pos_upper.config(state="disabled")
            row.pos_letter.config(state="disabled")
            row.neg_lower.config(state="disabled")
            row.neg_upper.config(state="disabled")
            row.neg_letter.config(state="disabled")

        if self.simulate_serial.get():
            self.serial_connection = FakeSerial()
        else:
            port = self.serial_var.get()
            if not port:
                messagebox.showerror("Error", "Seleccione un puerto serial.")
                self.enable_config_fields()
                return
            try:
                self.serial_connection = serial.Serial(port, 9600, timeout=1)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar al puerto: {e}")
                self.enable_config_fields()
                return

        self.running = True
        self.lbl_status.config(text="Estado: Conectado")
        self.btn_disconnect.config(state="normal")

        self.stream_conditions = []
        for row in self.condition_rows:
            data = row.get_data()
            if data is None:
                self.enable_config_fields()
                return
            self.stream_conditions.append(data)

        self.conditions_by_stream = {}
        for cond in self.stream_conditions:
            stream_id = cond["stream"]
            self.conditions_by_stream.setdefault(stream_id, []).append(cond)

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

        if self.simulate_serial.get():
            self.setup_log_viewers()
        else:
            if self.frame_logs:
                self.frame_logs.destroy()
                self.frame_logs = None

        self.last_samples = {stream_id: [] for stream_id in self.inlets.keys()}
        self.lsl_thread = threading.Thread(target=self.lsl_connection_loop, daemon=True)
        self.lsl_thread.start()

    def stop_connection(self):
        self.running = False
        self.lbl_status.config(text="Estado: Desconectado")
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.enable_config_fields()
        if not self.simulate_serial.get():
            try:
                self.serial_connection.close()
            except Exception:
                pass
        if self.frame_logs:
            self.frame_logs.destroy()
            self.frame_logs = None

    def enable_config_fields(self):
        self.btn_add_stream.config(state="normal")
        self.btn_remove_stream.config(state="normal")
        self.btn_refresh_all.config(state="normal")
        self.serial_menu.config(state="readonly")
        self.global_streams_menu.config(state="readonly")
        for row in self.condition_rows:
            row.stream_menu.config(state="readonly")
            row.pos_lower.config(state="normal")
            row.pos_upper.config(state="normal")
            row.pos_letter.config(state="normal")
            row.neg_lower.config(state="normal")
            row.neg_upper.config(state="normal")
            row.neg_letter.config(state="normal")

    def append_serial_console(self, text):
        self.serial_console.config(state="normal")
        self.serial_console.insert(tk.END, text)
        self.serial_console.see(tk.END)
        self.serial_console.config(state="disabled")

    def lsl_connection_loop(self):
        try:
            while self.running:
                for stream_id, inlet in self.inlets.items():
                    sample, _ = inlet.pull_sample(timeout=0.1)
                    if sample:
                        value = sample[0]
                        # Guardar historial para autoajuste
                        self.last_samples[stream_id].append(value)
                        if len(self.last_samples[stream_id]) > 500:
                            self.last_samples[stream_id] = self.last_samples[stream_id][-500:]
                        for cond in self.conditions_by_stream.get(stream_id, []):
                            # Condición positiva
                            if cond["pos_lower"] is not None and cond["pos_upper"] is not None:
                                if cond["pos_lower"] <= value <= cond["pos_upper"]:
                                    self.serial_connection.write(cond["pos_letter"].encode())
                                    if self.simulate_serial.get():
                                        msg = f"Valor {value:.2f} en [{cond['pos_lower']},{cond['pos_upper']}]: enviando '{cond['pos_letter']}' (Positivo)"
                                        self.master.after(0, self.update_log, stream_id, msg)
                                    if self.show_serial_console.get():
                                        self.master.after(0, self.append_serial_console, f"Enviado: {cond['pos_letter']}\n")
                            # Condición negativa
                            if cond["neg_lower"] is not None and cond["neg_upper"] is not None:
                                if cond["neg_lower"] <= value <= cond["neg_upper"]:
                                    self.serial_connection.write(cond["neg_letter"].encode())
                                    if self.simulate_serial.get():
                                        msg = f"Valor {value:.2f} en [{cond['neg_lower']},{cond['neg_upper']}]: enviando '{cond['neg_letter']}' (Negativo)"
                                        self.master.after(0, self.update_log, stream_id, msg)
                                    if self.show_serial_console.get():
                                        self.master.after(0, self.append_serial_console, f"Enviado: {cond['neg_letter']}\n")
                time.sleep(0.001)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error en hilo LSL", str(e))
            self.master.after(0, self.stop_connection)

    def toggle_serial_console(self):
        if self.show_serial_console.get():
            self.serial_console_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=0, sticky="we")
        else:
            self.serial_console_frame.grid_remove()

    def on_closing(self):
        self.stop_connection()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()