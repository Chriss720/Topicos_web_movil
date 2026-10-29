from functools import lru_cache
from pathlib import Path
from flask import Flask, jsonify, request
import joblib
import pandas as pd
from reglas import es_posible

app = Flask(__name__)

CARPETA_MODELO = Path(__file__).resolve().parent / "modelo"

MODELOS = {
    "arbol": {
        "archivo": "modelo_medios.joblib",
        "nombre": "Árbol de decisión",
        "etiqueta_motivo": "árbol de decisión",
    },
    "bosque": {
        "archivo": "modelo_bosque.joblib",
        "nombre": "Random Forest",
        "etiqueta_motivo": "random forest",
    },
    "red": {
        "archivo": "modelo_red.joblib",
        "nombre": "Red neuronal (MLP)",
        "etiqueta_motivo": "red neuronal",
    },
}

CAMPOS_NUMERICOS = [
    "distancia_km", "peso_kg", "largo_cm", "ancho_cm", "alto_cm", "volumen_l",
    "fragil", "refrigerado", "valor_declarado_mxn", "hora_salida",
]
CAMPOS_TEXTO = ["prioridad", "zona_destino", "clima", "trafico"]
CAMPOS = CAMPOS_NUMERICOS + CAMPOS_TEXTO


@lru_cache(maxsize=4)
def cargar_modelo(modelo_id: str):
    info = MODELOS[modelo_id]
    ruta = CARPETA_MODELO / info["archivo"]
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo de modelo no encontrado: {info['archivo']}")
    return joblib.load(ruta), info


@app.route("/salud", methods=["GET"])
def salud():
    return jsonify({"servicio": "recomendar", "estado": "ok"})


@app.route("/sugerir", methods=["POST"])
def sugerir():
    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return jsonify({"error": "el cuerpo debe ser un JSON válido"}), 400

    modelo_id = datos.get("modelo", "arbol") or "arbol"
    if modelo_id not in MODELOS:
        return jsonify({
            "error": f"modelo desconocido '{modelo_id}'",
            "modelos_disponibles": list(MODELOS.keys()),
        }), 400

    faltantes = [c for c in CAMPOS if c not in datos]
    if faltantes:
        return jsonify({"error": "faltan campos obligatorios", "campos": faltantes}), 400

    paquete = dict(datos)
    try:
        for c in CAMPOS_NUMERICOS:
            paquete[c] = float(paquete[c])
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"error en campo numérico: {str(e)}"}), 400

    try:
        modelo, info = cargar_modelo(modelo_id)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 503

    df = pd.DataFrame([paquete], columns=CAMPOS)
    probabilidades = modelo.predict_proba(df)[0]

    ranking = sorted(
        [
            {"medio": str(medio), "confianza": round(float(p), 3)}
            for medio, p in zip(modelo.classes_, probabilidades)
        ],
        key=lambda item: -item["confianza"],
    )

    preferido = ranking[0]["medio"]
    elegido = None
    confianza_elegida = 0.0

    for item in ranking:
        medio = item["medio"]
        if es_posible(medio, paquete):
            elegido = medio
            confianza_elegida = item["confianza"]
            break

    if elegido is None:
        elegido = "camioneta"
        motivo = "ningún medio sugerido era posible"
        corregido = True
    else:
        motivo = f"{info['etiqueta_motivo']}, confianza {confianza_elegida:.0%}"
        corregido = (elegido != preferido)
        if corregido:
            motivo += f"; se descartó {preferido} por las reglas del negocio"

    return jsonify({
        "servicio": "recomendar",
        "medio": elegido,
        "motivo": motivo,
        "preferido_por_modelo": preferido,
        "corregido_por_reglas": corregido,
        "modelo": modelo_id,
        "modelo_nombre": info["nombre"],
        "ranking": ranking,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
