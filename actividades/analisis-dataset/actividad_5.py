"""Actividad 5 — El dron es minoría: ¿hay que balancear el dataset?

Analiza el impacto del desbalanceo de clases (dron 9.5 % vs moto 45.8 %).
Evalúa y compara múltiples estrategias de balanceo (Undersampling, Oversampling, class_weight)
frente a los mismos 2 000 envíos de prueba fijos, mide sugerencias imposibles y demuestra
el efecto engañoso de la fuga de datos (data leakage).
"""

import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "proyectos", "dataset-medios"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from entrenar_arbol import NUMERICAS, CATEGORICAS, OBJETIVO
from usar_modelo import es_posible


def evaluar(x_tr, y_tr, x_pr, y_pr, nombre="Estrategia", class_weight=None):
    prep = ColumnTransformer([
        ("numericas", "passthrough", NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
    ])
    clf = DecisionTreeClassifier(
        max_depth=8, min_samples_leaf=5, random_state=42, class_weight=class_weight
    )
    mod = Pipeline([("preparacion", prep), ("arbol", clf)])
    mod.fit(x_tr, y_tr)

    pred = mod.predict(x_pr)
    acc = accuracy_score(y_pr, pred)
    prec_dron = precision_score(y_pr == "dron", pred == "dron", zero_division=0)
    rec_dron = recall_score(y_pr == "dron", pred == "dron", zero_division=0)
    n_dron_pred = int((pred == "dron").sum())

    df_eval = x_pr.assign(pred=pred)
    imposibles = int(df_eval.apply(lambda r: not es_posible(r["pred"], r), axis=1).sum())

    return {
        "Estrategia": nombre,
        "Envíos entrenamiento": len(x_tr),
        "Exactitud": f"{acc:.1%}",
        "Precision dron": f"{prec_dron:.3f}",
        "Recall dron": f"{rec_dron:.3f}",
        "Veces predice dron": n_dron_pred,
        "Sugerencias imposibles": imposibles,
    }


def main():
    csv_path = os.path.join(BASE_DIR, "envios_medios.csv")
    datos = pd.read_csv(csv_path)

    x = datos[NUMERICAS + CATEGORICAS]
    y = datos[OBJETIVO]

    # Partición fija estándar (mismos 2 000 envíos de prueba)
    x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )

    print("=" * 70)
    print("ACTIVIDAD 5 — EL DRON ES MINORÍA: ¿HAY QUE BALANCEAR?")
    print("=" * 70)

    # Parte A: Cálculos teóricos
    drones_test = (y_prueba == "dron").sum()
    motos_test = (y_prueba == "moto").sum()
    print("\n--- Parte A: Análisis antes de experimentar ---")
    print(f"Envíos de prueba: {len(y_prueba)} (Drones reales: {drones_test}, Motos reales: {motos_test})")
    acc_sin_dron = (len(y_prueba) - drones_test) / len(y_prueba)
    acc_solo_moto = motos_test / len(y_prueba)
    print(f"Exactitud de modelo trivial que NUNCA predice dron: {acc_sin_dron:.1%}")
    print(f"Exactitud de modelo trivial que SIEMPRE predice moto: {acc_solo_moto:.1%}")

    # Parte B: Evaluación de Estrategias
    resultados = []

    # 1. Sin balancear
    resultados.append(evaluar(x_entreno, y_entreno, x_prueba, y_prueba, "Sin balancear (Baseline)"))

    # 2. Submuestreo (Undersampling al tamaño de la minoritaria)
    df_tr = x_entreno.assign(target=y_entreno)
    min_count = int(df_tr["target"].value_counts()["dron"])
    df_under = pd.concat([g.sample(min_count, random_state=42) for _, g in df_tr.groupby("target")]).sample(frac=1.0, random_state=42)
    resultados.append(evaluar(df_under[NUMERICAS + CATEGORICAS], df_under["target"], x_prueba, y_prueba, "Submuestreo (Undersampling)"))

    # 3. Sobremuestreo (Oversampling de drones al nivel de moto)
    max_count = int(df_tr["target"].value_counts()["moto"])
    df_over_dron = df_tr[df_tr["target"] == "dron"].sample(max_count, replace=True, random_state=42)
    df_over = pd.concat([df_tr[df_tr["target"] != "dron"], df_over_dron]).sample(frac=1.0, random_state=42)
    resultados.append(evaluar(df_over[NUMERICAS + CATEGORICAS], df_over["target"], x_prueba, y_prueba, "Sobremuestreo (Oversampling)"))

    # 4. Ponderación por pesos en el árbol
    resultados.append(evaluar(x_entreno, y_entreno, x_prueba, y_prueba, "class_weight='balanced'", class_weight="balanced"))

    # 5. Trampa intencional (Data leakage previo al split)
    datos_trampa = pd.concat([datos, datos[datos[OBJETIVO] == "dron"].sample(4000, replace=True, random_state=42)])
    x_t = datos_trampa[NUMERICAS + CATEGORICAS]
    y_t = datos_trampa[OBJETIVO]
    x_tr_t, x_pr_t, y_tr_t, y_pr_t = train_test_split(x_t, y_t, test_size=0.2, stratify=y_t, random_state=42)
    resultados.append(evaluar(x_tr_t, y_tr_t, x_pr_t, y_pr_t, "Trampa (Leakage previo al split)"))

    print("\n--- Parte B: Comparativa de Estrategias de Balanceo ---")
    df_res = pd.DataFrame(resultados)
    print(df_res.to_string(index=False))


if __name__ == "__main__":
    main()
