"""Actividad 3 — Anatomía de los errores.

Estudia en profundidad los errores del árbol de decisión sobre el conjunto de prueba
(test_size=0.2, stratify=y, random_state=42). Identifica qué confusiones son más frecuentes,
el impacto de las reglas de negocio sobre los falsos positivos y qué distingue a los errores
de los aciertos.
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "proyectos", "dataset-medios"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from entrenar_arbol import NUMERICAS, CATEGORICAS, OBJETIVO
from usar_modelo import es_posible


def main():
    csv_path = os.path.join(BASE_DIR, "envios_medios.csv")
    datos = pd.read_csv(csv_path)

    x = datos[NUMERICAS + CATEGORICAS]
    y = datos[OBJETIVO]

    # Separación idéntica a la etapa de entrenamiento
    x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )

    modelo_path = os.path.join(BASE_DIR, "modelo_medios.joblib")
    modelo = joblib.load(modelo_path)
    prediccion = modelo.predict(x_prueba)

    df_eval = x_prueba.assign(real=y_prueba, predicho=prediccion)
    df_errores = df_eval[df_eval["real"] != df_eval["predicho"]]

    print("=" * 70)
    print("ACTIVIDAD 3 — ANATOMÍA DE LOS ERRORES")
    print("=" * 70)

    print(f"\nTotal envíos de prueba: {len(df_eval)}")
    print(f"Total aciertos: {(df_eval['real'] == df_eval['predicho']).sum()} ({(df_eval['real'] == df_eval['predicho']).mean():.1%})")
    print(f"Total errores: {len(df_errores)} ({len(df_errores) / len(df_eval):.1%})")

    # 1. Matriz de confusiones ordenada
    print("\n--- 1. Ranking de confusiones (Real -> Predicho) ---")
    confusiones = df_errores.groupby(["real", "predicho"]).size().sort_values(ascending=False)
    for (real, pred), cant in confusiones.items():
        print(f" - {real:10s} -> {pred:10s} : {cant:3d} envíos ({cant / len(df_errores):.1%} del total de errores)")

    # Confusión Extrema: Bicicleta vs Camioneta
    bici_a_camioneta = len(df_errores[(df_errores["real"] == "bicicleta") & (df_errores["predicho"] == "camioneta")])
    camioneta_a_bici = len(df_errores[(df_errores["real"] == "camioneta") & (df_errores["predicho"] == "bicicleta")])
    print(f"\nConfusión Bicicleta -> Camioneta: {bici_a_camioneta}")
    print(f"Confusión Camioneta -> Bicicleta: {camioneta_a_bici}")

    # 2. Análisis Moto -> Dron
    print("\n--- 2. Análisis de errores: Moto -> Dron ---")
    moto_dron = df_errores[(df_errores["real"] == "moto") & (df_errores["predicho"] == "dron")]
    noche_mask = (moto_dron["hora_salida"] < 6) | (moto_dron["hora_salida"] >= 21)
    print(f"Total errores Moto -> Dron: {len(moto_dron)}")
    print(f" - Ocurridos de noche (21:00 a 5:59): {noche_mask.sum()} ({noche_mask.mean():.1%})")

    corregidos_regla = moto_dron.apply(lambda r: not es_posible("dron", r), axis=1)
    print(f" - Errores corregidos automáticamente por es_posible(): {corregidos_regla.sum()} ({corregidos_regla.mean():.1%})")
    print(f" - Errores que pasarían el filtro de reglas de negocio: {(~corregidos_regla).sum()}")

    no_corregidos = moto_dron[~corregidos_regla]
    print("\nDetalle de los que NO corrigen las reglas (falsos positivos físicamente viables para dron):")
    print(no_corregidos[["distancia_km", "peso_kg", "volumen_l", "clima", "hora_salida", "prioridad"]].to_string())

    # 3. Análisis Moto -> Bicicleta
    print("\n--- 3. Análisis de errores: Moto -> Bicicleta ---")
    moto_bici = df_errores[(df_errores["real"] == "moto") & (df_errores["predicho"] == "bicicleta")]
    print(f"Total errores Moto -> Bicicleta: {len(moto_bici)}")
    print(f"Distancias (km): Min={moto_bici['distancia_km'].min():.2f}, Media={moto_bici['distancia_km'].mean():.2f}, Max={moto_bici['distancia_km'].max():.2f}")
    print(f"¿Alguna excede el límite de 7 km de bicicleta?: {(moto_bici['distancia_km'] > 7.0).any()}")

    bici_acertadas = df_eval[(df_eval["real"] == "bicicleta") & (df_eval["predicho"] == "bicicleta")]
    print("\nComparativa Bicis Acertadas vs Confusiones Moto -> Bici:")
    comp = pd.DataFrame({
        "Bicis Acertadas": [
            bici_acertadas["distancia_km"].mean(),
            bici_acertadas["peso_kg"].mean(),
            bici_acertadas["fragil"].mean() * 100,
            (bici_acertadas["clima"] == "lluvia").mean() * 100,
            (bici_acertadas["trafico"] == "alto").mean() * 100,
        ],
        "Moto -> Bici (Error)": [
            moto_bici["distancia_km"].mean(),
            moto_bici["peso_kg"].mean(),
            moto_bici["fragil"].mean() * 100,
            (moto_bici["clima"] == "lluvia").mean() * 100,
            (moto_bici["trafico"] == "alto").mean() * 100,
        ]
    }, index=["Distancia media (km)", "Peso medio (kg)", "% Frágil", "% Con lluvia", "% Con tráfico alto"])
    print(comp.round(2).to_string())


if __name__ == "__main__":
    main()
