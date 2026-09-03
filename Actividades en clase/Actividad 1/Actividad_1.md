# Actividad 1
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
   - Valida la sesión y bloquea peticiones duplicadas por doble clic antes de procesar el pago.

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
