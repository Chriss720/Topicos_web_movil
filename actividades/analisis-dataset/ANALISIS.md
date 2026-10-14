# Análisis del Dataset y del Modelo de Transporte

**Materia:** Tópicos Selectos de Tecnologías Web y Móvil  
**Ubicación:** `actividades/analisis-dataset/`  
**Archivo analizado:** `envios_medios.csv` (10,000 envíos)  
**Modelo usado:** `modelo_medios.joblib` (Árbol de decisión)

---

## ¿Cómo está organizado este reporte?

Para cada una de las 5 actividades seguimos 4 pasos muy sencillos:
1. **Predicción:** Qué pensábamos que iba a pasar antes de revisar los datos y por qué.
2. **Resultados:** Las tablas y números reales que salieron de la terminal.
3. **Explicación:** Qué pasó en realidad, comparando la predicción con los datos y explicando en qué nos equivocamos.
4. **Para pensar:** Nuestra conclusión y decisión explicada de forma clara y con argumentos.

---

## Actividad 1 — El retrato del dataset

### 1. Predicción
* **¿Qué medio domina cuando llueve?**  
  Pensábamos que la **camioneta**, porque es un vehículo cerrado y protege los paquetes del agua sin que el chofer se moje.
* **¿Y en el centro de la ciudad?**  
  La **bicicleta**, porque en el centro hay mucho tráfico, calles angostas y los viajes suelen ser de distancias muy cortas.
* **¿Cuál será la distancia más larga de una bicicleta?**  
  Creemos que **7 km**, porque es el límite máximo que fijan las reglas del negocio.
* **¿Habrá envíos que rompan las reglas en el archivo CSV?**  
  Creemos que **0**, porque el archivo se generó siguiendo las reglas del negocio.

---

### 2. Resultados

#### Porcentaje de medios según el clima
| Clima | Bicicleta | Camioneta | Dron | Moto |
|---|---|---|---|---|
| **Despejado** | 32.8% | 16.6% | 13.5% | 37.1% |
| **Lluvia** | 8.5% | 16.7% | 0.0% | **74.8%** |
| **Viento fuerte** | 31.7% | 18.4% | 0.0% | 49.9% |

#### Porcentaje de medios según la zona
| Zona | Bicicleta | Camioneta | Dron | Moto |
|---|---|---|---|---|
| **Centro** | **58.5%** | 13.5% | 0.0% | 28.0% |
| **Periferia** | 0.9% | 14.0% | 12.6% | **72.5%** |
| **Residencial** | 26.2% | 14.6% | 17.3% | 41.9% |
| **Rural** | 0.0% | 40.8% | 0.0% | **59.2%** |

#### Límites encontrados en los datos
* **Bicicleta:** Distancia de 0.37 a **7.00 km** | Peso de 0.1 a **8.0 kg** | Volumen de 0.3 a **39.7 L**.
* **Moto:** Distancia de 0.34 a **39.90 km** | Peso de 0.1 a **25.0 kg** | Volumen de 0.3 a **89.99 L**.
* **Dron:** Distancia de 2.07 a **14.99 km** | Peso de 0.1 a **2.5 kg** | Volumen de 0.3 a **11.98 L**.
* **Camioneta:** Distancia de 0.43 a **59.12 km** | Peso de 0.1 a **80.0 kg** | Volumen de 0.3 a **400.57 L**.

#### Revisión de reglas y casos especiales
* **Reglas rotas en el CSV:** **0 envíos (0.0%)**. Todas las filas respetan las reglas.
* **Bicicletas en la periferia:** Solo hubo **18 viajes (0.88%)**. Las distancias en la periferia van de 5.2 a 29.4 km, y el **97.8% de esos viajes superan los 7 km**.
* **Camionetas en viajes de menos de 2 km:** Hay **107 viajes**.
  * 36 llevan refrigeración (que solo la camioneta tiene).
  * 47 pesan más de 25 kg (no caben en moto).
  * 61 tienen un volumen de más de 90 L (muy grandes para moto).
  * **95 viajes (88.8%)** tienen una justificación física clara. Los 12 restantes se enviaron en camioneta por lluvia, urgencia o variación de costos.

---

### 3. Explicación

* **¿Por qué falló la predicción con lluvia?:** Pensábamos que saldrían más camionetas, pero la reina de la lluvia fue la **moto (74.8%)**. La razón es el **costo**: mover una camioneta es mucho más caro (gasolina y tarifa base). Un repartidor en moto con impermeable y mochila sellada puede llevar el paquete por una fracción del precio.
* **¿Dónde no vuela el dron?:**
  * Nunca vuela con **lluvia ni viento fuerte (0%)** porque el clima desestabiliza el dron o moja los circuitos.
  * Nunca vuela en el **centro (0%)** porque las leyes prohíben sobrevolar zonas con mucha gente, ni en zonas **rurales (0%)** porque quedan demasiado lejos.
* **¿Por qué la bicicleta casi no va a la periferia?:** No es que esté prohibido por una regla con ese nombre; es por la columna `distancia_km`. Como casi todos los viajes a la periferia son de más de 7 km, la bicicleta queda descartada automáticamente por distancia.
* **Límites que se ven y límites que no se ven:**
  * Los límites de la bici (7 km, 8 kg), de la moto (40 km, 25 kg) y del dron (15 km, 2.5 kg) se notan de inmediato al ver los números máximos del archivo.
  * El límite de la camioneta (1,000 kg o 1,000 km) **no se puede adivinar**, porque los paquetes normales de esta tienda no pasan de 80 kg ni de 60 km. La camioneta aguanta muchísimo más, pero los datos no muestran ese tope.

---

### 4. Para pensar

> **¿Podríamos reconstruir las reglas solo con los datos sin ver el manual? ¿Qué riesgo hay en dejar que una IA descubra las reglas sola?**

* Podríamos descubrir los límites de la bici, la moto y el dron, pero **no los de la camioneta** ni sabríamos con certeza si la refrigeración es exclusiva de la camioneta o si fue casualidad.
* **El gran riesgo de dejar que la IA invente las reglas:** La IA busca coincidencias estadísticas en los números, pero no tiene sentido común ni sabe de leyes. Si un día llega un paquete de 2.6 kg con sol, la IA podría mandarlo en dron creyendo que "casi le atina", poniendo en riesgo el dron de caerse sobre alguien.  
* **Conclusión:** Las reglas de seguridad y legales deben estar escritas como código fijo (como la función `es_posible`), para que sirvan de freno de mano y la IA nunca sugiera algo peligroso.

---

## Actividad 2 — La hora y el dron

### 1. Predicción
* **¿Cuántos drones salen a las 3:00 am?**  
  **0 drones**, porque de noche está prohibido que vuelen.
* **¿Qué porcentaje de paquetes sale de noche (antes de las 6 o después de las 21)?**  
  Calculamos entre un **10% y 15%**, ya que la gente hace la gran mayoría de sus compras durante el día.

---

### 2. Resultados

* **Drones a las 3:00 am:** **0**.
* **Horas donde no sale ningún dron:** De las **21:00 a las 5:00** (9 horas continuas en cero). Coincide exactamente con la regla nocturna.
* **Envíos de noche:** **1,053 viajes (10.5%)**.
* **Envíos de día:** **8,947 viajes (89.5%)**.
* **El cambio entre las 20:00 y las 21:00:**
  * A las 20:00 salen 115 bicis y 160 motos.
  * A las 21:00 las bicis caen a solo **20** y las motos suben a **240**.
* **Gráfica generada:** Guardada en `distribucion_horas.png`.

---

### 3. Explicación

* **¿Por qué caen las bicicletas a las 21:00?:** En el archivo de instrucciones (`README.md`) se indica que pedalear de noche es más peligroso, por lo que el sistema castiga a la bicicleta con un costo extra y prefiere asignar motocicletas.
* **¿Por qué a un árbol de decisión le cuesta entender la noche?:**
  * Los árboles solo pueden hacer preguntas simples de tipo: *"¿la hora es menor o igual a X?"*.
  * La noche está partida en dos en el reloj: la madrugada (de 0 a 5) y la noche tarde (de 21 a 23).
  * Para atrapar la noche, el árbol tiene que gastar al menos dos preguntas por separado (por ejemplo: ¿es menor a 6? y luego ¿es mayor a 20?). Eso le quita espacio para hacer preguntas sobre el peso o la distancia.

---

### 4. Para pensar

> **Diseñen una columna nueva para ayudarle al árbol con la noche y demuestren con números si sirvió.**

* **Diseño:** Creamos la columna `es_noche`. Vale `1` si la hora es menor a 6 o mayor o igual a 21, y vale `0` si es de día. Con esto, el árbol solo tiene que hacer una pregunta: *¿es_noche == 1?*.
* **Prueba numérica (con los mismos datos de prueba):**
  * Exactitud de noche con el modelo original: **81.74%**.
  * Exactitud de noche con la nueva columna: **94.06%** (¡subió más de 12 puntos!).
  * Exactitud global: subió de **92.10%** a **92.95%**.
* **Conclusión:** Ayudarle al modelo con una columna que resuma el horario nocturno elimina confusiones de raíz y mejora los resultados de inmediato.

---

## Actividad 3 — Anatomía de los errores

### 1. Predicción
* **¿Cuál será la confusión más común?**  
  Entre **moto y bicicleta**, porque atienden paquetes de tamaño parecido en distancias cortas.
* **¿Confundirá alguna vez bicicleta con camioneta?**  
  **No (0 veces)**, son vehículos totalmente diferentes en peso, tamaño y costo.

---

### 2. Resultados

* De 2,000 envíos de prueba, el modelo acertó 1,842 (92.1%) y falló en **158 (7.9%)**.
* **Las confusiones más frecuentes:**
  1. **Moto confundida con bicicleta:** 46 veces (29.1% de todos los errores).
  2. **Camioneta confundida con moto:** 32 veces (20.3%).
  3. **Moto confundida con dron:** 29 veces (18.4%).
  4. Bicicleta confundida con moto: 20 veces (12.7%).
  5. Dron confundido con bicicleta: 18 veces (11.4%).
  6. Camioneta con bici: 9 veces | Camioneta con dron: 4 veces.
  7. **Bicicleta confundida con camioneta:** **0 veces**.

#### Detalle de los errores:
* **Moto mandada en Dron (29 casos):**
  * **26 ocurrieron de noche (89.7%)**.
  * ¡Y las reglas fijas del negocio (`es_posible`) **corrigen automáticamente esos 26 errores**!
  * Solo 3 errores se le pasaron a las reglas: eran paquetes ligeros de día que físicamente cabían en dron, pero en el archivo se habían mandado en moto por ruido o centavos de diferencia.
* **Moto mandada en Bicicleta (46 casos):**
  * Distancia promedio: **4.08 km** (ninguna pasó de 7 km).
  * El factor clave fue el **clima**: en las bicis que el modelo acertó, solo el 2% tenía lluvia; pero en las motos que confundió con bici, **¡el 23.9% tenía lluvia!**.

---

### 3. Explicación

* Las confusiones ocurren entre "vecinos" de capacidad: moto con bici, camioneta con moto o moto con dron. Nunca confunde una bici con una camioneta.
* ¿Por qué confunde moto con bici bajo la lluvia? Porque el árbol ve que el paquete es liviano y que son pocos kilómetros, y se le olvida que cuando llueve la bicicleta se vuelve una mala opción. Priorizó la distancia y descuidó el clima.
* **¿Qué pasaría con otro `random_state`?:** Si cambiamos la semilla aleatoria, la prueba tendría otros paquetes al azar. Los porcentajes variarían poquito (tal vez 91.8% o 92.4%), pero las confusiones principales seguirían siendo exactamente las mismas.

---

### 4. Para pensar

> **Si solo pudieran corregir un tipo de error, ¿cuál elegirían y cómo lo arreglarían?**

* **Elegimos arreglar: Moto confundida con bicicleta (46 casos).**
* **¿Por qué?:** Porque el error de mandar dron de noche ya lo resuelven solos los filtros del negocio (`es_posible`). En cambio, mandar a un ciclista en vez de una moto bajo la lluvia **nadie lo frena**, porque la bici sí puede hacer 4 km físicamente. Eso termina en un repartidor empapado, paquetes mojados y entregas con retraso.
* **Cómo arreglarlo:** Modificando el modelo para que la variable de lluvia tenga más peso cuando la distancia sea corta.

---

## Actividad 4 — ¿Qué columnas usa de verdad el modelo?

### 1. Predicción
* **Columnas más importantes:** Pensamos que serían distancia, peso, volumen, si requiere refrigeración y clima.
* **Columnas que creemos que no usa:** Las medidas sueltas (largo, ancho, alto, porque ya tenemos el volumen) y el valor en dinero del paquete.

---

### 2. Resultados

#### Importancia real de cada columna en el árbol
1. **`distancia_km`**: 32.2%
2. **`volumen_l`**: 19.3%
3. **`clima`**: 14.4%
4. **`refrigerado`**: 13.1%
5. **`peso_kg`**: 12.6%
6. **`hora_salida`**: 5.9%
7. **`fragil`**: 2.0%
8. *Prioridad, valor en dinero, medidas sueltas, tráfico y zona de destino:* menos del 0.3% cada una (prácticamente cero).

#### Qué pasa si quitamos una columna (Ablación)
* Si quitamos **`distancia_km`**: la exactitud cae de 92.1% a **79.3%** (un golpe durísimo de -12.8%).
* Si quitamos **`clima`**: la exactitud cae a **84.5%** (-7.7%).
* Si quitamos **`refrigerado`**: la exactitud cae a **87.9%** (-4.3%).
* Si quitamos **`zona_destino`**, **`valor_declarado_mxn`** o **`trafico`**: la exactitud **no cambia nada (0.0%)**.

---

### 3. Explicación

* Las 4 columnas que dominan el árbol (`distancia`, `volumen`, `clima` y `refrigerado`) coinciden exactamente con las primeras preguntas que hace el árbol en sus ramas principales.
* **¿Por qué la zona de destino tiene importancia 0 y aun así nunca se manda un dron al centro?:**
  1. Porque el centro tiene distancias cortitas que el árbol ya manda en bici.
  2. Porque en el código de la plataforma hay una regla escrita a mano que dice: *si va al centro, el dron está prohibido*. La regla protege la operación sin que el árbol tenga que gastar preguntas en eso.

---

### 4. Para pensar

> **Si la app pide 14 datos y el modelo casi no usa varios de ellos, ¿deberíamos dejar de pedirlos?**

* **Respuesta: No, no hay que quitarlos.**
* Aunque la IA no use esos datos para decidir el vehículo, el negocio los necesita para otras cosas igual de importantes:
  * La **zona de destino** se necesita para saber si es legal volar el dron.
  * El **valor del paquete** se necesita para cobrar el seguro si se pierde.
  * Las **medidas de la caja (largo, ancho, alto)** se necesitan para saber si el paquete cabe por la puerta del vehículo, aunque el volumen en litros sea chico.
  * El **tráfico** servirá en el futuro para calcular tiempos estimados de entrega en una versión mejorada del sistema.

---

## Actividad 5 — El dron es minoría: ¿hay que balancear el dataset?

### 1. Parte A — Pensar antes de tocar los datos

* **Modelos simplones:**
  * Si hiciéramos un modelo tramposo que **nunca diga dron** y le atine a todo lo demás, tendría una exactitud del **90.5%** (porque solo hay 9.5% de drones).
  * Si un modelo dijera **siempre moto**, tendría **45.8%**.
  * Esto demuestra que la exactitud general engaña: un modelo inútil que no sabe qué es un dron parece tener más de 90% de calificación. Por eso hay que medir la **precisión** (cuántos de los que llamó dron realmente lo eran) y el **recall** (cuántos de los drones reales logró encontrar).
* **¿Por qué hay tan pocos drones?:** No es un error de recolección de datos; es la realidad del negocio. Los drones solo pueden llevar cosas muy livianas, de día, sin lluvia y fuera del centro.
* **¿Dónde se balancea?:** Solo en los datos de **entrenamiento**. El conjunto de prueba **nunca se toca**, porque debe representar el mundo real tal cual es.

---

### 2. Parte B — Probar estrategias

Comparamos todas las opciones contra los mismos 2,000 paquetes de prueba:

| Estrategia | Envíos para entrenar | Exactitud | Precisión Dron | Recall Dron | Drones predichos | Sugerencias imposibles |
|---|---|---|---|---|---|
| **Sin balancear (Original)** | 8,000 | **92.1%** | **0.839** | 0.905 | 205 | **31** |
| **Submuestreo (Borrar motos y bicis)** | 3,032 | 89.8% | 0.889 | 0.932 | 199 | 29 |
| **Sobremuestreo (Duplicar drones)** | 10,905 | 90.0% | 0.728 | **1.000** | 261 | **54** |
| **`class_weight='balanced'`** | 8,000 | 90.2% | 0.766 | **1.000** | 248 | **35** |
| *Trampa (Duplicar antes de separar prueba)* | 11,200 | *93.4%* | *0.948* | *0.994* | *1,038* | *43* |

> **Sobre la trampa:** Al duplicar drones antes de apartar la prueba, el modelo parece tener 93.4% de exactitud. Es una **mejora falsa**: el modelo simplemente memorizó copias idénticas que estaban repetidas en el examen.

---

### 3. Parte C — Interpretar

* **El costo de balancear:** Cuando forzamos al modelo a ver muchos drones (con sobremuestreo o pesos), el modelo aprende a ver drones por todos lados: predice 261 drones (cuando solo había 190 reales). Su precisión cae a 0.728 y las **sugerencias imposibles se disparan a 54**.
* **El costo de borrar datos (Submuestreo):** Para igualar las clases tuvimos que tirar a la basura casi 5,000 ejemplos de motos y camionetas, haciendo que el modelo aprenda peor y baje a 89.8%.
* **¿Por qué sobremuestreo y `class_weight` dan casi lo mismo?:** Porque en el fondo hacen la misma matemática: castigar con más fuerza al árbol cada vez que no detecta un dron.
* **Pérdida de la confianza:** Cuando el modelo balanceado dice "tengo 84% de seguridad de que esto es un dron", ese porcentaje ya no refleja la realidad de la calle, sino el mundo inflado del laboratorio.

---

### 4. Parte D — Decidir

> **¿La empresa debería usar el modelo balanceado en la plataforma real?**

* **Recomendación: NO, debemos quedarnos con el modelo sin balancear.**
* **Razones de negocio:**
  1. Mandar un dron por error es peligroso y caro. El modelo balanceado predice demasiados drones que no caben o no pueden volar (54 sugerencias imposibles).
  2. El modelo normal (sin balancear) funciona muy bien (92.1% de exactitud) y sus pocos fallos nocturnos quedan frenados en seco por las reglas del negocio.
  3. **¿Qué pasa si la empresa compra el doble de drones mañana?:** No cambia nada. Duplicar la flota de drones no hace que los paquetes pesen menos ni evita que llueva. El dron seguirá estando limitado por el peso y el clima, así que balancear a la fuerza seguiría siendo un error.

---

## Conclusiones finales

1. **El mejor equipo de trabajo:** El Machine Learning es excelente para encontrar el medio más económico, pero las **reglas fijas de negocio** son indispensables para garantizar la seguridad y las leyes.
2. **La exactitud no lo es todo:** En problemas del mundo real hay que revisar dónde se equivoca el modelo y cuánto cuesta cada error.
3. **Ayudarle al modelo con datos claros (`es_noche`)** funciona mucho mejor que intentar trucos artificiales de balanceo.
