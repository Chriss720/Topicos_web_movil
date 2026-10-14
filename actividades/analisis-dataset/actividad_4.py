"""Actividad 4 — ¿Qué columnas usa de verdad el modelo?

Analiza la importancia de características (feature_importances_) del árbol de decisión,
realiza un estudio de ablación (entrenamiento sin cada columna para evaluar impacto en exactitud)
y examina por qué ciertas variables como 'zona_destino' tienen importancia cero a pesar
de las restricciones operativas.
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "proyectos", "dataset-medios"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from entrenar_arbol import NUMERICAS, CATEGORICAS, OBJETIVO


def main():
    csv_path = os.path.join(BASE_DIR, "envios_medios.csv")
    datos = pd.read_csv(csv_path)

    x = datos[NUMERICAS + CATEGORICAS]
    y = datos[OBJETIVO]

    x_entreno, x_prueba, y_entreno, y_prueba = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
    )

    modelo_path = os.path.join(BASE_DIR, "modelo_medios.joblib")
    modelo = joblib.load(modelo_path)

    print("=" * 70)
    print("ACTIVIDAD 4 — ¿QUÉ COLUMNAS USA DE VERDAD EL MODELO?")
    print("=" * 70)

    # 1. Feature importances individuales
    arbol = modelo.named_steps["arbol"]
    prep = modelo.named_steps["preparacion"]
    nombres_features = prep.get_feature_names_out()
    importancias_ind = pd.Series(arbol.feature_importances_, index=nombres_features).sort_values(ascending=False)

    print("\n--- 1. Importancia individual de cada feature generada (Top 12) ---")
    print(importancias_ind.head(12).round(4).to_string())

    # 2. Agrupación por columna original
    importancias_col = {}
    for col in NUMERICAS:
        importancias_col[col] = importancias_ind.get(f"numericas__{col}", 0.0)
    for col in CATEGORICAS:
        prefijo = f"categoricas__{col}_"
        importancias_col[col] = sum([val for key, val in importancias_ind.items() if key.startswith(prefijo)])

    df_col_imp = pd.Series(importancias_col).sort_values(ascending=False)
    print("\n--- 2. Importancia agrupada por columna original (suma = 1.0) ---")
    print(df_col_imp.round(4).to_string())

    # 3. Estudio de ablación (Ablation Study)
    acc_base = accuracy_score(y_prueba, modelo.predict(x_prueba))
    print(f"\nExactitud base con todas las columnas: {acc_base:.2%}")
    print("\n--- 3. Estudio de ablación: impacto en exactitud al omitir cada columna ---")

    impactos = {}
    for col in NUMERICAS + CATEGORICAS:
        sub_num = [c for c in NUMERICAS if c != col]
        sub_cat = [c for c in CATEGORICAS if c != col]

        prep_sub = ColumnTransformer([
            ("numericas", "passthrough", sub_num),
            ("categoricas", OneHotEncoder(handle_unknown="ignore"), sub_cat),
        ])
        pipe_sub = Pipeline([
            ("preparacion", prep_sub),
            ("arbol", DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=42))
        ])
        pipe_sub.fit(x_entreno[sub_num + sub_cat], y_entreno)
        acc_sub = accuracy_score(y_prueba, pipe_sub.predict(x_prueba[sub_num + sub_cat]))
        impactos[col] = {
            "Exactitud": f"{acc_sub:.2%}",
            "Delta Exactitud": f"{(acc_sub - acc_base):+.2%}",
            "Impacto": "Crítico" if (acc_base - acc_sub) > 0.03 else ("Moderado" if (acc_base - acc_sub) > 0.005 else "Nulo / Mínimo")
        }

    df_ablation = pd.DataFrame(impactos).T
    print(df_ablation.to_string())


if __name__ == "__main__":
    main()
