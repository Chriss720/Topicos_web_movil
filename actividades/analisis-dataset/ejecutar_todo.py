"""Ejecutor maestro de todas las actividades de análisis del dataset.

Ejecuta secuencialmente:
- Actividad 1: El retrato del dataset
- Actividad 2: La hora y el dron
- Actividad 3: Anatomía de los errores
- Actividad 4: Importancia de columnas y ablación
- Actividad 5: Balanceo del dataset y estudio de clases minoritarias
"""

import sys
import subprocess
import os

SCRIPTS = [
    "actividad_1.py",
    "actividad_2.py",
    "actividad_3.py",
    "actividad_4.py",
    "actividad_5.py"
]

def main():
    directorio = os.path.dirname(os.path.abspath(__file__))
    print("=" * 80)
    print("EJECUTANDO SUITE COMPLETA DE ANÁLISIS DE DATASET Y MODELO")
    print("=" * 80)
    
    for script in SCRIPTS:
        ruta = os.path.join(directorio, script)
        print(f"\n>>> Iniciando {script}...")
        res = subprocess.run([sys.executable, ruta], cwd=directorio)
        if res.returncode != 0:
            print(f"Error al ejecutar {script} (código {res.returncode})")
            sys.exit(res.returncode)
            
    print("\n" + "=" * 80)
    print("¡TODAS LAS ACTIVIDADES SE EJECUTARON SATISFACTORIAMENTE!")
    print("Consulte el archivo ANALISIS.md para el reporte detallado.")
    print("=" * 80)

if __name__ == "__main__":
    main()
