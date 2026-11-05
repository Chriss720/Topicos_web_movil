# Análisis de Arquitectura - Proyecto E

## Comentarios Generales del Proyecto
El proyecto presenta una arquitectura monolítica sin separación de capas:
- Mezcla de consultas SQL, HTML y lógica de negocio en los mismos archivos (index1.php, kardex1.php, pagar1.php).
- Antipatrón de integración en pagar.php con un switch de 30 casos para bancos.
- Vulnerabilidades de seguridad graves como eval() en api.php e inyección SQL en login1.php.
- Código duplicado masivo (2,000 funciones idénticas en funciones.php y 50 tablas vacías en la BD).

## Misión 1 - El portal no es un patrón

| Problema | Capa | Patrón que corresponde | Por qué ese y no el vecino más fácil de confundir | Cuándo NO aplicaría |
| :--- | :--- | :--- | :--- | :--- |
| switch con 30 integraciones bancarias (pagar.php) | Integración | Strategy / Adapter | Strategy permite intercambiar el proveedor de pago en tiempo de ejecución. No es Facade porque Facade simplifica un subsistema existente, no intercambia algoritmos equivalentes. | Si solo existe un método de pago fijo y nunca habrá variaciones. |
| Consultas SQL directas en las vistas (kardex.php, index1.php) | Datos | Repository | Repository representa una colección en memoria aislando el dominio del SQL. No es Active Record porque Active Record junta la entidad con las consultas SQL. | En aplicaciones CRUD muy simples sin lógica de negocio. |
| Envío de correo síncrono al pagar (pagar1.php) | Aplicación / Dominio | Observer | Observer notifica el evento PagoRealizado de forma desacoplada. No es Chain of Responsibility porque este último pasa la petición en serie para ser procesada en cadena. | Cuando el envío de correo sea obligatorio e indispensable para mantener la transacción síncrona. |
| Verificación manual de sesión en cada archivo (login1.php, index1.php) | Políticas Transversales | Intercepting Filter | Intercepting Filter procesa peticiones previas de forma transversal (sesión/logs). No es Front Controller porque Front Controller se encarga del enrutamiento central. | Cuando sea una validación exclusiva de un único endpoint muy específico. |
| eval() y lectura directa de archivos en api.php | Integración | Command | Command encapsula peticiones en objetos con parámetros explícitos y seguros. No es Interpreter porque Interpreter evalúa gramáticas/código dinámico no controlado. | Cuando se requiera un motor de scripting dinámico real donde no se conozcan las instrucciones. |
| Actualización directa de saldos sin transacciones (pagar1.php) | Aplicación / Dominio | Unit of Work | Unit of Work mantiene el seguimiento de cambios y coordina la escritura final atómicamente. No es Transaction Script porque este ejecuta sentencias SQL aisladas. | En operaciones de solo lectura donde no hay modificaciones a la base de datos. |

## Misión 2 - Una petición, varios patrones (Pagar la inscripción)

Flujo en orden de la petición POST:

1. Recepción HTTP (POST /pagar): Router central -> Front Controller (Punto de entrada único).
2. Filtros previos: Middleware de sesión y auditoría -> Intercepting Filter (Valida sesión e inicia logs).
3. Mapeo de entrada: Request DTO / Command -> DTO / Command (Encapsula y valida los datos de entrada).
4. Coordinación del proceso: Servicio de aplicación -> Application Service (Orquesta la ejecución del caso de uso).
5. Procesamiento de pago: Pasarela de pago -> Strategy / Adapter (Conecta con la API del banco seleccionado).
6. Persistencia: Repositorio e historia de transacciones -> Repository y Unit of Work (Guarda cambios en BD de forma atómica).
7. Notificación: Publicador de eventos -> Observer (Dispara el evento post-pago para enviar correo y registrar bitácora).

## Misión 3 - Políticas transversales

### 1. ¿Cuándo corresponde Front Controller y por qué?
Corresponde cuando la aplicación necesita centralizar todas las peticiones HTTP en un solo punto de entrada. Sirve para gestionar el enrutamiento, la inicialización del sistema y la captura global de errores, evitando duplicar código en múltiples archivos PHP.

### 2. ¿Qué mecanismo ya ofrece Spring, Laravel o Express?
- Spring: DispatcherServlet y HandlerInterceptor / Filters.
- Laravel: public/index.php y la canalización de Middleware.
- Express: El router de la app y la pila de funciones Middleware (app.use).

### 3. Orden de la cadena y justificación de la autenticación

Orden propuesto:
1. Bitácora (Logging)
2. Autenticación
3. Cupo de inscripciones (Regla de negocio)
4. Caso de uso (Pago y persistencia)

Justificación: Autenticar después del cobro es un error de diseño porque realizarías transacciones bancarias reales a usuarios no identificados o no autorizados. Si la autenticación falla al final, el dinero ya fue cobrado y el sistema queda inconsistente. Además, viola el principio de seguridad donde las políticas transversales deben proteger la ejecución del dominio desde el inicio.

### 4. ¿Qué NO debe hacer esa cadena?
No debe contener reglas de negocio ni lógica del dominio (como calcular promedios o validar cupos académicos). La cadena solo debe encargarse de aspectos técnicos y de infraestructura (sesiones, logs, CORS, seguridad).
