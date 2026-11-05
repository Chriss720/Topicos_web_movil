# Actividad 1 — Análisis de Arquitectura y Patrones de Diseño
**Materia:** Tópicos Selectos de Tecnologías Web y Móvil

---

## Misión 1 — El portal no es un patrón

| Problema | Capa | Patrón | Por qué este y no el vecino | Cuándo NO usarlo | Ya lo trae el marco |
|---|---|---|---|---|---|
| 1. Sesión y bitácora duplicada en 40 archivos de trámites. | Políticas transversales | Chain of Responsibility / Middleware | vs Decorator: La petición pasa por varios manejadores en orden antes del núcleo. Decorator envuelve objetos individuales. | Si un solo manejador atiende siempre o la lógica depende del caso de uso. | Middleware de Express, Django, filtros de Spring. |
| 2. Script pagar.php con switch gigante para adaptar bancos. | Integración | Adapter (+ Strategy) | vs Facade: API ajena (banco) no coincide con lo que el dominio espera (00/01 vs acreditado); traduce sin tocar código extranjero. Facade simplifica un subsistema propio ruidoso. | Si se controlan ambos lados y se puede cambiar la interfaz de origen. | Convertidores de Retrofit/Jackson, mapeos DTO. |
| 3. Consultas SQL dentro de las plantillas del kardex y constancias. | Datos | Repository | vs Active Record: Repository separa las consultas SQL de las vistas y modelos. Active Record deja la BD pegada al modelo. | En reportes de solo lectura pesados donde conviene SQL directo a DTO. | ORMs como Spring Data JPA, Eloquent, Prisma. |
| 4. Pago hace llamadas síncronas (correo, caja) y doble clic cobra dos veces. | Aplicación / Dominio | Observer (Domain Events) + Idempotency Key | vs Observer síncrono / Llamada directa: Varios interesados se enteran del cambio sin que al sujeto le importe (desacoplado). Si falla el correo, la llamada directa rompe el pago. | Si es un solo llamador directo o si las acciones deben ser 100% atómicas en la BD. | EventEmitter, Eventos del DOM, Event Bus. |
| 5. App móvil hace 12 peticiones para inicio y kiosco requiere HTML. | Presentación / Integración | Backend for Frontend (BFF) / Facade | vs Facade de dominio: BFF adapta y junta la respuesta según el cliente (JSON móvil vs HTML kiosco). Facade simplifica el backend interno. | Si la app y el kiosco consumen la misma estructura de datos sin cambios. | API Gateway en el borde o controladores por cliente. |
| 6. Caída de banco y CURP congela la página e impide consultar Kardex. | Integración | Circuit Breaker (Proxy) | vs Retry: Retry reintenta y satura más los hilos del servidor; Circuit Breaker frena llamadas y da respuesta de contingencia. | Si no hay política de fallo o si la API externa es 100% obligatoria sin fallback. | Proxy de red, API Gateway. |

---

## Misión 2 — Una petición, varios patrones

**Caso de uso:** Pagar la inscripción (`POST /pagos`)

1. **Intercepción HTTP:** Middleware (`Chain of Responsibility` / `Intercepting Filter`)
   - Valida la sesión activa y bloquea peticiones duplicadas por doble clic antes de procesar el pago.

2. **Enrutamiento:** Router (`Front Controller`)
   - Recibe `POST /pagos` y mapea la petición al controlador correspondiente.

3. **Controlador:** PagoController (`Controller MVC`)
   - Recibe el DTO con los datos del pago y delega la ejecución al servicio de aplicación.

4. **Orquestación:** PagoService (`Application Service` / `Transaction Script`)
   - Abre la transacción, coordina la validación, el cobro en banco y la persistencia.

5. **Integración Bancaria:** PasarelaPagoAdapter (`Adapter` + `Strategy`)
   - Traduce la petición al protocolo y códigos del banco seleccionado.

6. **Persistencia:** PagoRepository (`Repository` + `Unit of Work`)
   - Guarda la entidad Pago acreditada en la base de datos dentro de la transacción.

7. **Notificación Asíncrona:** EventPublisher (`Observer` / `Domain Events`)
   - Publica `PagoAcreditadoEvent` para hacer el alta de materias, correo y aviso a caja en segundo plano.

8. **Respuesta HTTP:** JSONResponse (`DTO`)
   - Retorna `200 OK` con el folio y estado del pago de inmediato.

---

## Misión 3 — Políticas transversales

### 1. ¿Cuándo corresponde Front Controller y por qué?
Corresponde cuando una aplicación web maneja múltiples rutas y páginas que comparten necesidades comunes (autenticación, manejo de sesiones, formato de respuesta, captura global de errores).
- **Por qué:** Centraliza la recepción de todas las peticiones HTTP en un único punto de entrada en lugar de tener 40 scripts independientes. Esto permite aplicar políticas transversales de forma uniforme y enrutar las solicitudes a sus controladores sin duplicar infraestructura.

### 2. ¿Qué mecanismo ya ofrece Spring, Laravel o Express para no escribir un frontal casero?
Los marcos modernos ya instancian este patrón de fábrica:
- **Spring:** `DispatcherServlet` (Front Controller) junto con `HandlerInterceptor` / `OncePerRequestFilter`.
- **Laravel:** Punto de entrada único `public/index.php` con el enrutador y la cadena de `HTTP Middleware` (`Kernel.php`).
- **Express:** El objeto `app` y la tubería de `app.use(middleware)`.
- **Conclusión:** No se debe implementar una clase `FrontController` ni una estructura `ChainOfResponsibility` casera en GoF, ya que el marco de trabajo ya lo gestiona de forma transparente.

### 3. Orden propuesto de la cadena de políticas transversales
1. **Autenticación / Sesión:** Validar la identidad y la validez del token/sesión del usuario.
2. **Bitácora (Logging):** Registrar la petición entrante ya asociada al usuario autenticado.
3. **Cupo de inscripciones (Filtro preliminar de tráfico):** Verificar disponibilidad general antes de iniciar operaciones pesadas.
4. **Caso de Uso (Controlador / Dominio):** Ejecutar la lógica de negocio y el cobro.

> **Justificación de seguridad:** Autenticar *después* del cobro es un **error de diseño crítico**. La autenticación es una precondición de la infraestructura que asegura que el solicitante tiene permiso para operar. Ejecutar primero el cobro implica realizar operaciones financieras irreversibles a usuarios anónimos o no autorizados antes de saber si tienen derecho a realizar la transacción.

### 4. ¿Qué NO debe hacer esa cadena? (Las políticas transversales no son el reglamento)
La cadena de middlewares **no debe contener lógica de dominio ni reglas de negocio** (el "reglamento" universitario).
- **Lo que SÍ hace la cadena:** Manejo de protocolo HTTP, validación de tokens de sesión, formato de cabeceras, logging de red y límite de peticiones (rate limiting).
- **Lo que NO debe hacer:** No debe validar prerrequisitos académicos, ni calcular costos de inscripción, ni aplicar descuentos, ni modificar entidades de la base de datos. Esas reglas pertenecen a la **capa de aplicación/dominio** (servicios de dominio). Mezclar reglas de negocio en los filtros acopla la lógica al protocolo HTTP e impide reutilizarla en otros canales (como comandos CLI, tareas en segundo plano o APIs secundarias).

---

## Análisis General de Anti-patrones en el Código del Proyecto (`proyectoe`)

1. **Acoplamiento por copia y pega (Punto 1):** 40 archivos independientes copiando validación de sesión y encabezados HTML. Solución: Usar el router y middlewares del marco.
2. **Violación de Abierto/Cerrado en Pagos (Punto 2):** Script `pagar.php` con `switch` de 200 líneas. Solución: Aplicar el patrón **Adapter** por banco e inyectarlo vía **Strategy**.
3. **Falta de capa de persistencia (Punto 3):** SQL embebido directamente en las plantillas HTML del kardex. Solución: Abstraer las consultas dentro de la capa de datos mediante **Repository**.
4. **Acoplamiento síncrono de efectos secundarios (Punto 4):** El flujo de pago llama directamente y en el mismo hilo a correo y alta de materias. Solución: Usar **Domain Events (Pub-Sub)** asíncronos y añadir **Idempotency Key** para evitar cobros dobles por clics repetidos.
5. **Falta de adaptación por tipo de cliente (Punto 5):** 12 peticiones de la app móvil. Solución: Crear endpoints orientados al cliente mediante **BFF (Backend for Frontend)**.
6. **Propagación de fallos en cascada (Punto 6):** Caídas de APIs externas (banco/CURP) bloquean la consulta del Kardex. Solución: Aislar servicios externos con **Circuit Breaker** y **Fallback**.
7. **Sobreingeniería (Punto 7):** Propuestas de Event Sourcing y CQRS para la descarga simple de constancias en PDF. Solución: Mantener un flujo de lectura directo simple y sin complejidad innecesaria.
