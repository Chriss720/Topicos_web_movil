"""Actividad 1 — El retrato del dataset.

Explora el comportamiento general del dataset, distribución por clima y zona,
límites físicos de cada medio y validación contra las reglas de negocio.
"""

import os
import sys
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "proyectos", "dataset-medios"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from usar_modelo import LIMITES, es_posible


def main():
    csv_path = os.path.join(BASE_DIR, "envios_medios.csv")
    datos = pd.read_csv(csv_path)

    print("=" * 70)
    print("ACTIVIDAD 1 — EL RETRATO DEL DATASET")
    print("=" * 70)

    # 1. Porcentaje de medios por clima
    print("\n--- 1. Distribución porcentual por clima (pd.crosstab normalize='index') ---")
    ct_clima = pd.crosstab(datos["clima"], datos["medio_recomendado"], normalize="index") * 100
    print(ct_clima.round(2).to_string())

    # 2. Porcentaje de medios por zona de destino
    print("\n--- 2. Distribución porcentual por zona de destino ---")
    ct_zona = pd.crosstab(datos["zona_destino"], datos["medio_recomendado"], normalize="index") * 100
    print(ct_zona.round(2).to_string())

    # 3. Límites numéricos reales (distancia, peso, volumen) por medio
    print("\n--- 3. Resumen numérico (min, median, max) por medio ---")
    resumen_num = datos.groupby("medio_recomendado")[["distancia_km", "peso_kg", "volumen_l"]].agg(["min", "median", "max"])
    print(resumen_num.round(2).to_string())

    # 4. Bicicleta en periferia
    print("\n--- 4. Análisis de la bicicleta en periferia ---")
    bici_periferia = datos[(datos["medio_recomendado"] == "bicicleta") & (datos["zona_destino"] == "periferia")]
    dist_periferia = datos[datos["zona_destino"] == "periferia"]["distancia_km"]
    print(f"Total de bicis enviadas a periferia: {len(bici_periferia)}")
    print(f"Distancias en periferia: Min={dist_periferia.min():.2f} km, Mediana={dist_periferia.median():.2f} km, Max={dist_periferia.max():.2f} km")
    pct_mayor_7km = (dist_periferia > 7.0).mean() * 100
    print(f"Porcentaje de envíos a la periferia con distancia > 7 km: {pct_mayor_7km:.2f}%")

    # 5. Validación contra reglas de negocio con es_posible
    print("\n--- 5. Validación contra reglas del negocio (es_posible) ---")
    cumple = datos.apply(lambda fila: es_posible(fila["medio_recomendado"], fila), axis=1)
    rotas = len(datos) - cumple.sum()
    print(f"Envíos totales: {len(datos)}")
    print(f"Envíos que rompen las reglas de negocio en el CSV: {rotas} ({rotas / len(datos):.2%})")

    # 6. Camionetas en viajes cortos (< 2 km)
    print("\n--- 6. Camionetas en viajes de menos de 2 km ---")
    camionetas_cortas = datos[(datos["medio_recomendado"] == "camioneta") & (datos["distancia_km"] < 2.0)]
    print(f"Total camionetas con distancia < 2 km: {len(camionetas_cortas)}")
    
    just_refrig = (camionetas_cortas["refrigerado"] == 1).sum()
    just_peso = (camionetas_cortas["peso_kg"] > 25.0).sum()
    just_vol = (camionetas_cortas["volumen_l"] > 90.0).sum()
    justificadas_estricto = camionetas_cortas[
        (camionetas_cortas["refrigerado"] == 1) | 
        (camionetas_cortas["peso_kg"] > 25.0) | 
        (camionetas_cortas["volumen_l"] > 90.0)
    ]
    sin_just = len(camionetas_cortas) - len(justificadas_estricto)
    
    print(f" - Con cadena de frío (refrigerado=1): {just_refrig}")
    print(f" - Con sobrepeso para moto (peso > 25 kg): {just_peso}")
    print(f" - Con sobredimensión para moto (volumen > 90 L): {just_vol}")
    print(f" - Total justificadas por carga/frío: {len(justificadas_estricto)} ({len(justificadas_estricto)/len(camionetas_cortas):.1%})")
    print(f" - Sin restricción física insuperable (asignadas por costo/lluvia/ruido): {sin_just}")


if __name__ == "__main__":
    main()
