# ✨ Carro Bluetooth EOG

Este repositorio contiene toda la información y el código necesarios para **controlar un carro** utilizando señales *EOG (electrooculograma)* horizontales. El sistema se basa en el control de dos motores mediante dos comandos simples, utilizando comunicación **UART** a través de **Bluetooth**.

---

## 📋 Descripción

El proyecto integra los siguientes componentes:

- **🔹 Señales EOG (horizontal):** Solo se utilizan dos comandos para controlar el movimiento.
- **🔸 Tarjeta de control:** `Cyton_OpenVibe_Python_ComunicacionUART_Bluetooth`, que facilita la comunicación entre el procesamiento de las señales y el Arduino.
- **🔹 Arduino Nano:** Interfaz principal para el control de los motores.
- **🔸 Módulo HC-05 (Bluetooth):** Permite la comunicación inalámbrica mediante UART.
- **🔹 Driver TB66:** Controla los motores (referidos como "motores amarillos").
- **🔸 Voltaje:** Operación del carro con una fuente de **9V**.

Este sistema demuestra cómo se pueden emplear señales biológicas para controlar dispositivos físicos, abriendo paso a aplicaciones en áreas como la domótica y la asistencia para personas con movilidad reducida.

---

## ⭐ Características

- **💡 Control innovador:** Utiliza señales EOG horizontales para dirigir el movimiento.
- **⚙️ Simplicidad:** Solo dos comandos para un control eficaz del vehículo.
- **📶 Conectividad Bluetooth:** Comunicación confiable y sin cables a través del módulo HC-05.
- **🔧 Integración de hardware y software:** Combina Arduino Nano, driver TB66 y procesamiento en Python para lograr un sistema integrado.
- **🎥 Documentación visual:** Video explicativo para facilitar la comprensión del funcionamiento.

---

## 🛠️ Instalación y Uso

1. **🔌 Hardware:**  
   Conecta los componentes siguiendo el esquemático incluido en el repositorio. Asegúrate de contar con una fuente de **9V** para alimentar el carro.

2. **💻 Software:**  
   Configura el entorno **Python** y **OpenVibe** siguiendo las instrucciones. Instala las librerías necesarias para la comunicación **UART**.

3. **⚙️ Configuración:**  
   Ajusta los parámetros en el código para que coincidan con tu configuración de hardware.

4. **🚀 Ejecución:**  
   Inicia el sistema y utiliza los comandos EOG para controlar el movimiento del carro.

---

## 🎬 Recursos Adicionales

Para una explicación detallada del funcionamiento del sistema, consulta el siguiente video en YouTube:  
[Tutorial Carro EOG](https://www.youtube.com/watch?v=coV044tbprE)

---

## 📄 Licencia

Proyecto OpenSource.
