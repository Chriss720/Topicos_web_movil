from django.http import HttpResponse, JsonResponse
from .reglas import elegir_medio


def hola(request):
    return HttpResponse("Hola. Plataforma de entregas (aún sin pedidos).")


def estado(request):
    return JsonResponse({
        "servicio": "entregas",
        "version": 1,
        "medios_disponibles": ["camioneta", "moto", "bicicleta", "dron"],
    })


def cotizar(request):
    # 1. Leer los datos de la petición (que llegan como texto)
    km_str = request.GET.get("km")
    kg_str = request.GET.get("kg")

    # 2. Validar que no falten y que sean números positivos
    if km_str is None or kg_str is None:
        return JsonResponse({"error": "Faltan los parámetros 'km' y/o 'kg'"}, status=400)

    try:
        km = float(km_str)
        kg = float(kg_str)
        if km < 0 or kg < 0:
            raise ValueError
    except ValueError:
        return JsonResponse({"error": "Los parámetros deben ser números positivos válidos"}, status=400)

    # 3. Llamar a la regla de negocio
    resultado = elegir_medio(km, kg)

    # 4. Devolver la respuesta en JSON
    return JsonResponse({
        "km": km,
        "kg": kg,
        "medio": resultado["medio"],
        "motivo": resultado["motivo"]
    })
