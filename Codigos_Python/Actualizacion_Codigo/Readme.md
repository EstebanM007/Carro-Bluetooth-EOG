
## Resumen

Crear un entorno virtual te permite aislar dependencias de cada proyecto y mantener tu sistema limpio. En Windows usarás el módulo `venv`, la terminal integrada de VS Code y la paleta de comandos para seleccionar el intérprete adecuado.

---

## 1. Verificar Python instalado 🔍

Abre PowerShell y ejecuta `python --version` para confirmar que tienes Python 3.x instalado en tu sistema.

---

## 2. Abrir tu proyecto en VS Code 📂

Inicia VS Code y ve a **Archivo > Abrir carpeta...** para seleccionar (o crear) la carpeta raíz de tu proyecto.

---

## 3. Crear el entorno virtual 🏗️

En la terminal integrada de VS Code (Terminal > Nueva terminal), ejecuta:

```powershell
python -m venv .venv
```

Esto genera la carpeta oculta `.venv` con un intérprete aislado para tu proyecto.

---

## 4. Activar el entorno virtual ✅

* En **PowerShell**:

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

  Si da error, ajusta la política con:

  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```
* En **CMD**:

  ```cmd
  .venv\Scripts\activate.bat
  ```

Verás el prefijo `(.venv)` en el prompt indicando que el entorno está activo.

---

## 5. Seleccionar el intérprete en VS Code 🔧

Pulsa `Ctrl+Shift+P`, escribe **Python: Select Interpreter**, y elige

```
.venv\Scripts\python.exe
```

Así VS Code usará tu entorno virtual para ejecución, linting y depuración.

---

## 6. Instalar dependencias 📦

Con el entorno activo, crea o actualiza `requirements.txt` con tus librerías. Luego ejecuta:

```powershell
pip install -r requirements.txt
```

Esto instala los paquetes dentro de `.venv` sin afectar el Python global.

---

## 7. Probar el entorno 🧪

Crea `test.py` con:

```python
import sys
print("Entorno virtual activo:", sys.executable)
```

Ejecuta `python test.py`; debe mostrar la ruta dentro de `.venv` y confirmar el aislamiento.

---

## 8. Desactivar y reactivar 🔄

* **Desactivar**:

  ```powershell
  deactivate
  ```
* **Reactivar** (cuando regreses al proyecto):

  * PowerShell: `.venv\Scripts\Activate.ps1`
  * CMD: `.venv\Scripts\activate.bat`
    De este modo vuelves a tu entorno virtual en cualquier sesión ([Medium]).

---

¡Y eso es todo! Ahora tu proyecto en Windows utiliza un entorno virtual en VS Code, manteniendo las dependencias organizadas y aisladas. 🚀
