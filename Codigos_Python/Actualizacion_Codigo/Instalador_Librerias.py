#!/usr/bin/env python
import sys
import subprocess

try:
    # Para Python 3.8+ utiliza importlib.metadata
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Para versiones anteriores, se usa pkg_resources
    import pkg_resources
    def version(pkg_name):
        return pkg_resources.get_distribution(pkg_name).version
    PackageNotFoundError = Exception

def get_installed_version(pkg_name):
    """
    Intenta obtener la versión instalada probando varias variantes en el nombre.
    Esto sirve, por ejemplo, para detectar 'pyserial' aunque se registre como 'PySerial'.
    """
    variants = [pkg_name, pkg_name.lower(), pkg_name.capitalize(), "PySerial"]
    for variant in variants:
        try:
            return version(variant)
        except PackageNotFoundError:
            continue
    raise PackageNotFoundError(f"No se encontró el paquete {pkg_name}.")

def install(package_spec):
    """
    Instala el paquete utilizando pip.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
    except subprocess.CalledProcessError as e:
        print(f"Error instalando {package_spec}: {e}")
        sys.exit(1)

# Diccionario con los paquetes y la versión exacta a instalar.
dependencies = {
    "pyserial": "3.5",
    "pylsl": "1.17.6"
}

print("Verificando dependencias...\n")
for package, required_version in dependencies.items():
    try:
        installed_version = get_installed_version(package)
        if installed_version == required_version:
            print(f"El paquete '{package}' (versión {installed_version}) ya está instalado.")
        else:
            print(f"El paquete '{package}' tiene la versión {installed_version} y se requiere la versión {required_version}.")
            respuesta = input(f"¿Deseas actualizar '{package}' a la versión {required_version}? [S/n]: ").strip().lower()
            if respuesta == "" or respuesta.startswith("s"):
                install(f"{package}=={required_version}")
                print(f"'{package}=={required_version}' instalado correctamente.")
                print("Por favor, reinicia el script para reflejar la actualización.")
                sys.exit(0)
            else:
                print(f"No se actualizó '{package}'. Se mantiene la versión {installed_version} instalada.")
    except PackageNotFoundError:
        print(f"El paquete '{package}' no fue encontrado.")
        respuesta = input(f"¿Deseas instalar '{package}' en la versión {required_version}? [S/n]: ").strip().lower()
        if respuesta == "" or respuesta.startswith("s"):
            install(f"{package}=={required_version}")
            print(f"'{package}=={required_version}' instalado correctamente.")
            print("Por favor, reinicia el script para reflejar la instalación.")
            sys.exit(0)
        else:
            print(f"El paquete '{package}' no fue instalado.")

print("\nProceso de verificación de dependencias finalizado.")
