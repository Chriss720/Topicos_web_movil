def elegir_medio(km, kg):
    """
    Decide el medio de entrega basado en la distancia (km) y el peso (kg).
    """
    if kg > 20:
        return {"medio": "camioneta", "motivo": "paquete pesado (más de 20 kg)"}
    elif km <= 3 and kg <= 5:
        return {"medio": "dron", "motivo": "distancia muy corta y paquete muy ligero"}
    elif km <= 10 and kg <= 10:
        return {"medio": "bicicleta", "motivo": "distancia y peso adecuados para bicicleta"}
    else:
        return {"medio": "moto", "motivo": "distancia media o paquete que no cabe en bici"}
