"""Actividad 2 — La hora y el dron.

Analiza el comportamiento temporal de los envíos, las restricciones nocturnas
del dron, la sustitución de bicicleta por moto en la noche y el impacto de
diseñar una característica para el árbol (feature engineering: es_noche).
"""

import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "proyectos", "dataset-medios"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from entrenar_arbol import NUMERICAS, CATEGORICAS, OBJETIVO


def main():
    csv_path = os.path.join(BASE_DIR, "envios_medios.csv")
    datos = pd.read_csv(csv_path)

    print("=" * 70)
    print("ACTIVIDAD 2 — LA HORA Y EL DRON")
    print("=" * 70)

    # 1. Tabla cruzada de hora vs medio recomendado
    print("\n--- 1. Envíos por hora y medio recomendado ---")
    ct_hora = pd.crosstab(datos["hora_salida"], datos["medio_recomendado"])
    print(ct_hora.to_string())

    # 2. Drones a las 3:00 y horas sin drones
    drones_3am = ct_hora.loc[3, "dron"] if 3 in ct_hora.index else 0
    print(f"\nDrones que salen a las 3:00: {drones_3am}")
    horas_cero_dron = ct_hora[ct_hora["dron"] == 0].index.tolist()
    print(f"Horas sin ningún dron: {horas_cero_dron}")

    # 3. Comparativa día vs noche
    noche = datos[(datos["hora_salida"] < 6) | (datos["hora_salida"] >= 21)]
    dia = datos[(datos["hora_salida"] >= 6) & (datos["hora_salida"] < 21)]
    print(f"\nTotal envíos de noche (21:00 a 5:59): {len(noche)} ({len(noche) / len(datos):.1%})")
    print(f"Total envíos de día (6:00 a 20:59): {len(dia)} ({len(dia) / len(datos):.1%})")

    # 4. Transición 20:00 a 21:00 (Bicicleta vs Moto)
    print("\n--- Transición 19:00, 20:00 y 21:00 ---")
    sub_horas = ct_hora.loc[[19, 20, 21], ["bicicleta", "moto", "camioneta", "dron"]]
    print(sub_horas.to_string())

    # 5. Generar gráfica de barras apiladas
    output_img = os.path.join(os.path.dirname(__file__), "distribucion_horas.png")
    fig, ax = plt.subplots(figsize=(10, 5))
    ct_hora.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    ax.set_title("Distribución de Medios de Transporte por Hora de Salida")
    ax.set_xlabel("Hora de salida (0 a 23)")
    ax.set_ylabel("Cantidad de envíos")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    fig.savefig(output_img, dpi=150)
    plt.close(fig)
    print(f"\nGráfica guardada en: {output_img}")

    # 6. Para pensar: Feature Engineering de 'es_noche'
    print("\n--- 6. Evaluación de Feature Engineering (columna 'es_noche') ---")
    datos["es_noche"] = ((datos["hora_salida"] < 6) | (datos["hora_salida"] >= 21)).astype(int)

    # Entrenar modelo estándar vs modelo con es_noche
    x = datos[NUMERICAS + CATEGORICAS]
    y = datos[OBJETIVO]
    x_tr, x_pr, y_tr, y_pr = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)

    prep_base = ColumnTransformer([
        ("num", "passthrough", NUMERICAS),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS)
    ])
    clf_base = DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)
    pipe_base = Pipeline([("prep", prep_base), ("arbol", clf_base)])
    pipe_base.fit(x_tr, y_tr)
    acc_base = accuracy_score(y_pr, pipe_base.predict(x_pr))

    # Modelo con columna 'es_noche' agregada a NUMERICAS
    num_noche = NUMERICAS + ["es_noche"]
    x_noche = datos[num_noche + CATEGORICAS]
    x_tr_n, x_pr_n, y_tr_n, y_pr_n = train_test_split(x_noche, y, test_size=0.2, stratify=y, random_state=42)

    prep_noche = ColumnTransformer([
        ("num", "passthrough", num_noche),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS)
    ])
    clf_noche = DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42)
    pipe_noche = Pipeline([("prep", prep_noche), ("arbol", clf_noche)])
    pipe_noche.fit(x_tr_n, y_tr_n)
    pred_noche = pipe_noche.predict(x_pr_n)
    acc_noche = accuracy_score(y_pr_n, pred_noche)

    # Medir errores específicos en horario nocturno
    mask_noche_pr = (x_pr["hora_salida"] < 6) | (x_pr["hora_salida"] >= 21)
    acc_noche_sub_base = accuracy_score(y_pr[mask_noche_pr], pipe_base.predict(x_pr)[mask_noche_pr])
    acc_noche_sub_nueva = accuracy_score(y_pr_n[mask_noche_pr], pred_noche[mask_noche_pr])

    print(f"Exactitud global modelo base: {acc_base:.2%}")
    print(f"Exactitud global con 'es_noche': {acc_noche:.2%}")
    print(f"Exactitud exclusiva en envíos nocturnos (Base): {acc_noche_sub_base:.2%}")
    print(f"Exactitud exclusiva en envíos nocturnos (Con 'es_noche'): {acc_noche_sub_nueva:.2%}")


if __name__ == "__main__":
    main()
