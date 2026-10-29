import os
import time
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

RECOMENDAR_URL = os.getenv("RECOMENDAR_URL", "http://recomendar:8002").rstrip("/")

pedidos_db = []


@app.route("/salud", methods=["GET"])
def salud():
    return jsonify({
        "servicio": "pedidos",
        "estado": "ok",
        "recomendar_url": RECOMENDAR_URL,
        "pedidos_registrados": len(pedidos_db),
    })


@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    datos = request.get_json(silent=True)
    if not datos or not isinstance(datos, dict):
        return jsonify({"error": "el cuerpo debe ser un JSON válido"}), 400

    modelo_solicitado = datos.get("modelo", "arbol")
    medio = None
    motivo = None
    preferido = None
    corregido = False
    plan_b = False
    detalle_ia = None

    # Intentar obtener la recomendación llamando al microservicio de IA por red
    try:
        url_sugerir = f"{RECOMENDAR_URL}/sugerir"
        resp = requests.post(url_sugerir, json=datos, timeout=3.5)
        if resp.status_code == 200:
            rec = resp.json()
            medio = rec.get("medio", "moto")
            motivo = rec.get("motivo", "Sugerido por IA")
            preferido = rec.get("preferido_por_modelo")
            corregido = rec.get("corregido_por_reglas", False)
            detalle_ia = rec
        else:
            plan_b = True
            medio = "camioneta"
            motivo = f"Plan B: recomendador respondió HTTP {resp.status_code}"
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        # Fallo parcial: Recomendar está caído o timeout, pero Pedidos sigue vivo
        plan_b = True
        medio = "camioneta"
        motivo = "Plan B de contingencia: servicio de recomendación (IA) no disponible"

    folio = f"ENV-{len(pedidos_db) + 1001:04d}"
    nuevo_pedido = {
        "folio": folio,
        "medio": medio,
        "motivo": motivo,
        "modelo": modelo_solicitado,
        "preferido_por_modelo": preferido,
        "corregido_por_reglas": corregido,
        "plan_b": plan_b,
        "creado_en": time.strftime("%Y-%m-%d %H:%M:%S"),
        "paquete": {
            "distancia_km": datos.get("distancia_km"),
            "peso_kg": datos.get("peso_kg"),
            "hora_salida": datos.get("hora_salida"),
        },
    }

    pedidos_db.append(nuevo_pedido)

    respuesta = dict(nuevo_pedido)
    if detalle_ia:
        respuesta["detalle_ia"] = detalle_ia

    return jsonify(respuesta), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
