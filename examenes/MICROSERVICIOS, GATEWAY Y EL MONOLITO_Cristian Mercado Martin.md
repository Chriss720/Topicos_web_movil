# Examen: Microservicios, Gateway y el Monolito con API
**Materia:** Tópicos Selectos de Tecnologías Web y Móvil  
**Profesor:** Eduardo Alcaraz  
**Alumno:** Cristian Mercado Martin  

---

### Pregunta 1, inciso a: Desarmar el argumento del compañero sobre qué cree cumplir con la API, qué cree cumplir con Docker y en qué se equivoca en cada una
Él cree que con la API cumple con la primera parte de separar a los clientes del servidor, y en parte tiene razón porque una API separa la interfaz de la lógica, pero se equivoca al pensar que tener una API significa hacer microservicios, ya que solo está definiendo un camino para pedir datos mientras todo sigue viviendo adentro del mismo código. Con Docker cree que cumple con la segunda parte de separar servidores entre sí, pero ahí se equivoca por completo porque meter su programa en un contenedor solo es guardarlo en una caja para moverlo fácil; no está separando servidores entre sí porque adentro de esa misma caja todo el sistema sigue corriendo junto en el mismo proceso y si algo falla se cae todo.

### Pregunta 1, inciso b: Contraejemplo mínimo de código Django con API y Docker que siga siendo monolito, y qué partir para que deje de serlo
Un contraejemplo mínimo es un proyecto de Django que tenga las carpetas de usuarios, compras y productos en el mismo código, usando Django REST Framework para devolver datos en JSON y corriendo dentro de un solo contenedor de Docker con una base de datos SQLite. Aunque tenga API y use Docker sigue siendo un monolito al cien por ciento porque todo corre en el mismo proceso de memoria, así que para que deje de serlo tendríamos que partir el sistema sacando, por ejemplo, el módulo de compras a su propio proyecto con su propio contenedor y base de datos independiente, de modo que cada uno corra por separado y si uno se apaga el otro siga vivo.

### Pregunta 1, inciso c: Si la frase habla de tecnologías (Docker, REST) o de límites de proceso y despliegue, defendiendo la lectura
La frase habla de límites de proceso y de despliegue, y no de tecnologías en específico. Esto se debe a que no importa qué herramientas uses como Docker, máquinas virtuales, Django o scripts normales, lo importante es dónde se cortan las fronteras de ejecución: la API define el límite entre quien pide el servicio desde el celular o navegador y quien lo atiende en el servidor, mientras que los microservicios marcan el límite entre diferentes programas que corren en procesos separados y que se pueden apagar, reiniciar o actualizar por su cuenta sin tirar al resto del sistema.

---

### Pregunta 2, inciso a: Separar las ideas de rutas frente a réplicas, explicando qué resuelve y qué no resuelve cada una
Las rutas en el código resuelven únicamente la organización interna de los caminos de la aplicación para saber qué función atiende a qué dirección web, pero no resuelven la separación del sistema porque todas las rutas viven en el mismo programa y si una se traba o consume toda la memoria afecta a las demás. Por su parte, las réplicas resuelven la capacidad de atender a más personas al mismo tiempo y tener respaldo si una copia se apaga, pero no resuelven crear microservicios porque son simplemente tres clones idénticos del mismo monolito, por lo que si hay un error en el código de pedidos va a fallar exactamente igual en las tres réplicas.

### Pregunta 2, inciso b: Si una de las tres réplicas se cae a mitad de un POST /pedidos, si el sistema dejó de ser monolito y por qué
No dejó de ser monolito porque lo único que se tiene son tres copias idénticas del mismo programa funcionando al mismo tiempo, lo que se conoce como un monolito replicado. Cada una de las réplicas sigue conteniendo adentro todo el código de usuarios, pedidos y recomendaciones revuelto, por lo que el hecho de que una réplica se apague en plena compra no significa que el sistema se haya dividido en piezas independientes, sino simplemente que se cayó una de las tres copias completas.

### Pregunta 2, inciso c: Rediseño con palabras del archivo compose para ilustrar microservicios y cantidad mínima de imágenes requeridas
Para rediseñarlo como microservicios tendríamos un servicio de gateway para recibir las visitas de los usuarios y repartir las llamadas, un servicio de usuarios para manejar cuentas y accesos, un servicio de pedidos para crear y guardar las compras, y un servicio de recomendación para calcular sugerencias con el modelo. Se necesitarían como mínimo cuatro imágenes distintas porque cada microservicio debe tener su propio código, sus propias dependencias y su ciclo de vida independiente, ya que si todos usaran la misma imagen seguiría siendo el mismo monolito repetido con nombres diferentes.

---

### Pregunta 3, inciso a: Si es realmente un gateway, usando la analogía del recepcionista y explicando qué oficios se mezclaron
No es un gateway, sino un monolito amontonado en un solo contenedor al que le pusieron ese nombre por error. Es exactamente como contratar a un recepcionista en una oficina para que reciba a los clientes y revise sus credenciales, pero al mismo tiempo ponerlo a cocinar la comida, trapear los pisos, cobrar en la caja y salir en bicicleta a repartir cartas. En este diseño mezclaron el trabajo del recepcionista que revisa la seguridad y entrega la página, con el de logística que elige el transporte con el archivo de machine learning, el de cajero que guarda los pedidos en la base de datos y el de cartero que manda los correos.

### Pregunta 3, inciso b: Tres consecuencias malas de este diseño cuando el modelo se reentrena cada semana y el correo empieza a fallar
La primera consecuencia es que si el servidor de correos se traba o se vuelve lento, toda la petición del usuario se queda congelada impidiendo que se termine la compra; la segunda es que cada semana que se reentrena y actualiza el archivo pesado del modelo hay que reiniciar todo el contenedor, tirando por completo la entrada del sistema y dejando a todos los clientes sin acceso; y la tercera es que el modelo de machine learning consume muchísima memoria y procesador al hacer cálculos, lo que satura el contenedor y bloquea la base de datos SQLite al querer guardar compras al mismo tiempo.

### Pregunta 3, inciso c: Partir el contenedor en piezas mínimas explicando cuáles quedan en el borde y cuáles detrás
En el borde únicamente dejamos el gateway, que es la entrada ligera que valida el token de seguridad, sirve la página web básica y redirige las llamadas hacia los servicios de atrás. Detrás del borde colocamos el servicio de pedidos para guardar las compras en la base de datos, el servicio de recomendación que guarda el archivo del modelo para calcular el transporte sin saturar la entrada, y un servicio de notificaciones que mande los correos de confirmación en segundo plano para que si falla no congele la compra del usuario.

---

### Pregunta 4, inciso a: Por qué falla la conexión a 127.0.0.1 en Compose y a qué proceso apunta desde dentro de Pedidos
Falla porque en Docker cada contenedor funciona como si fuera una computadora independiente con su propia red interna y su propia casa. Desde adentro del contenedor de Pedidos la dirección 127.0.0.1 apunta a sí mismo y busca el puerto 8002 en su propio espacio donde no hay nada corriendo, en lugar de buscar en el contenedor de Recomendar, por lo que la conexión es rechazada de inmediato aunque el otro servicio esté funcionando perfectamente en su propio contenedor.

### Pregunta 4, inciso b: Por qué tiene chance de funcionar http://recomendar:8002 y quién inventa ese nombre
Funciona porque Docker Compose crea una red compartida entre todos los contenedores del archivo y cuenta con un traductor de nombres interno. El nombre lo inventa el DNS interno de Docker, el cual toma el nombre que le pusimos al servicio en el archivo de configuración y lo traduce automáticamente a la dirección de red que le asignó a ese contenedor para que puedan encontrarse sin tener que memorizar números.

### Pregunta 4, inciso c: URL para la laptop de otro alumno (192.168.0.57), condiciones en la WiFi y qué puede seguir fallando
La dirección que pondríamos sería http://192.168.0.57:8002, y para que funcione en la WiFi es necesario que la red no tenga activado el aislamiento entre dispositivos para que permita que dos computadoras se comuniquen, y que el firewall de la laptop del compañero tenga abierto el puerto 8002 para conexiones entrantes. Si solo cambiamos la dirección puede seguir fallando que el programa del compañero esté configurado para escuchar solo peticiones locales en localhost en lugar de escuchar a toda la red con 0.0.0.0, lo que rechazaría nuestra conexión, o que el módem le cambie la IP a su laptop al reconectarse.

---

### Pregunta 5, inciso a: Tiempo de espera del cliente en hora normal y quién pone el tiempo dominante
En una hora normal el cliente espera aproximadamente 205 milisegundos, que es la suma de los 200 milisegundos que tarda el servicio de Recomendar más los 5 milisegundos que agrega el gateway en pasar la petición. El tiempo dominante lo pone por completo el servicio de Recomendar con sus 200 milisegundos, ya que es el proceso más pesado y lento de toda la cadena mientras que el resto responde casi de inmediato.

### Pregunta 5, inciso b: Qué ve el cliente en el 5% con falla y qué «mentira útil» se está aceptando con el plan B
El cliente ve que su pedido se creó con éxito y recibe una respuesta positiva sin enterarse de que hubo una falla interna. La mentira útil que estamos aceptando es asignarle un medio de transporte fijo por defecto, como la moto, aunque quizá no sea el más barato ni el más eficiente para su paquete en ese momento, asumiendo ese pequeño costo con tal de salvar la venta y no dejar al usuario con una pantalla de error.

### Pregunta 5, inciso c: Consecuencias de reintentar 10 veces con timeout de 3 segundos si Recomendar cae 10 minutos frente al Plan B
Si reintentamos diez veces con esperas de tres segundos cada petición se quedará trabada durante más de treinta segundos, lo que causará que las mil peticiones que llegan por hora se vayan amontonando en la memoria y se acaben las conexiones libres del servidor. Esto provoca que el gateway y el servicio de pedidos colapsen por completo y se caiga el sistema entero para todos los usuarios. El Plan B no es peor que reintentar, sino todo lo contrario; cuando un servicio se cae, el Plan B responde rápido con una alternativa aceptable y libera los servidores para que la tienda siga vendiendo, mientras que reintentar a ciegas solo ahoga y remata al sistema.

---

### Pregunta 6, experimento 1: Qué pasa si se apaga el gateway con docker compose stop gateway
Al apagar el gateway el navegador muestra una pantalla de error de conexión rechazada y no se puede cargar la página ni hacer ningún pedido porque se cerró la única entrada. Por dentro de la red tanto el servicio de pedidos como el de recomendación siguen completamente vivos y funcionando con normalidad, listos para responder si algún otro programa interno les mandara mensajes.

### Pregunta 6, experimento 2: Qué pasa si se apaga pedidos con docker compose stop pedidos
Al apagar pedidos la página principal sí carga en el navegador porque el gateway sigue vivo, pero al momento de presionar el botón para crear un pedido la pantalla muestra un error del servidor porque el gateway no encuentra a nadie que guarde la compra. Por dentro del sistema el gateway sigue atendiendo visitas y el servicio de recomendación sigue vivo y disponible para hacer cálculos si alguien le pregunta.

### Pregunta 6, experimento 3: Qué pasa si se apaga recomendar con docker compose stop recomendar
Al apagar recomendación la página carga normalmente y la compra sí se completa con éxito porque el servicio de pedidos activa el Plan B y asigna la moto por defecto, aunque la respuesta tarda unos tres segundos extras por esperar el tiempo límite antes de aplicar el respaldo. Por dentro del sistema tanto el gateway como el servicio de pedidos siguen completamente prendidos y operando para los clientes.

### Pregunta 6, conclusión: En cuál parece más muerto hacia afuera y qué enseña esto sobre el borde
El sistema parece mucho más muerto en el primer experimento al apagar el gateway, ya que hacia afuera parece que todo el sistema colapsó por completo aunque la mayor parte de los servicios y la lógica sigan sanos por dentro. Esto nos enseña que el borde es la cara visible y la única puerta de entrada al sistema, por lo que si el borde se cae no importa qué tan buenos sean los servidores de atrás para el usuario no existe nada, lo que exige que el gateway sea muy ligero, simple y confiable.

---

### Pregunta 7, inciso a: Problema de diseño que introdujo Diana al levantar un segundo gateway
Diana rompió el principio de tener una sola puerta de entrada y le pasó el problema de decidir a dónde conectarse al cliente. Es como poner dos puertas principales en una casa sin nadie que organice el paso, obligando a los usuarios a adivinar qué dirección usar; además, no hay nada que coordine a ambos gateways, por lo que si Ana actualiza una regla o cambia la página y Diana no, los clientes verán comportamientos totalmente distintos según a qué dirección le peguen.

### Pregunta 7, inciso b: Por qué falla el localhost de Beto y cómo se corrige sin juntar los servicios en su máquina
Falla porque al usar localhost la computadora de Beto busca el servicio en sí misma, pero el programa de recomendación ya no está en su máquina sino en la de Carla, por lo que la conexión se rechaza. Se corrige cambiando la variable de configuración en la máquina de Beto para poner la dirección IP que tiene Carla en la red WiFi y su puerto correspondiente, asegurándose de que Carla tenga el servicio prendido y su firewall permita conexiones entrantes.

### Pregunta 7, inciso c: WiFi del campus con aislamiento entre clientes y propuesta de plan B de laboratorio
No se puede hacer la práctica tal cual en esa red porque el aislamiento bloquea cualquier mensaje directo entre las computadoras de los alumnos. El plan B más rápido es que un alumno active la zona WiFi compartida de su celular para conectar ahí todas las laptops, ya que los teléfonos no bloquean la comunicación entre aparatos locales, o bien correr los servicios dentro de una sola computadora usando contenedores en Docker Compose, lo cual mantiene la misma lección de procesos separados comunicándose por red interna sin depender del internet de la escuela.

---

### Pregunta 8, inciso a: Tres problemas de llamar directo a Recomendar y Pedidos desde el navegador saltándose el gateway
Este diseño presenta problemas graves de seguridad porque obliga a abrir los puertos de todos los servicios a internet y configurar permisos de conexión en cada uno, exponiendo las direcciones privadas de los servidores en el navegador del cliente. También crea una dependencia muy frágil con las direcciones de red, ya que si un servidor cambia de máquina o de número hay que actualizar el código de la página web de todos los usuarios. Además, rompe la consistencia del negocio porque si la llamada para pedir la recomendación funciona pero la de guardar el pedido falla por la red, se queda un cálculo volando y la compra no se concreta, dejando al cliente confundido sin saber qué pasó.

### Pregunta 8, inciso b: Secuencia correcta con gateway desde una sola llamada y por qué no debe hablar el navegador con Recomendar
La secuencia correcta es que el navegador haga una sola petición al gateway enviando los datos del pedido, el gateway le pase la orden al servicio de pedidos, y sea este último quien llame internamente por red privada a recomendación para pedir el transporte. Una vez que pedidos tiene el transporte o aplica el plan B si falla, guarda la compra en su base de datos y le responde éxito al gateway para que le confirme al cliente. El navegador no debe hablar con recomendación porque al cliente solo le interesa comprar, mientras que consultar algoritmos y aplicar planes de respaldo es una regla interna del negocio que debe estar protegida en el backend.

### Pregunta 8, inciso c: Quién debe crear el folio y qué invariante se rompe si ambos servicios crean algo
El folio debe ser creado únicamente por el servicio de pedidos porque es el dueño de la información de las compras y de la base de datos de órdenes. Si ambos servicios intentan crear algo se rompe la regla de folio único y la consistencia del sistema, provocando compras con números duplicados o pedidos con dos identificadores diferentes; peor aún, si recomendación inventa un folio antes de que la orden se guarde y la compra falla después, quedarían registros de folios fantasma de compras que en realidad nunca se hicieron.

---

### Pregunta 9, inciso a: Crítica al nombre cerebro, corte de oficios y choque de tiempos entre el LLM y el despacho
Llamar al servicio cerebro es un mal diseño porque es un nombre comodín donde se amontona cualquier cosa que use inteligencia artificial sin una función clara, mezclando dos oficios totalmente distintos como la logística de calcular un transporte y el marketing de convencer al cliente con un texto bonito. Esto causa que el sistema de envíos colapse porque amarraron una tarea crítica de despacho que debe responder en menos de medio segundo a un texto de ventas que tarda ocho segundos en generarse, congelando la salida de los paquetes por esperar un texto que ni siquiera necesitan para repartir la caja.

### Pregunta 9, inciso b: Propuesta de dos endpoints y qué parte del sistema usa cada uno
Se deben separar en dos servicios o rutas diferentes: una ruta de marketing para pedirle al modelo de lenguaje el texto de convencimiento, la cual es utilizada por la pantalla de la tienda cuando el cliente está viendo el producto antes de comprar, y una ruta de logística para calcular el transporte con el modelo numérico rápido, la cual es llamada únicamente por el flujo de pedidos cuando el cliente ya pagó y se necesita preparar el paquete de inmediato.

### Pregunta 9, inciso c: Dónde debe apuntar el front de tienda y qué archivo tocar si cambian de proveedor de LLM
El front de la tienda debe apuntar siempre al gateway para no exponer la dirección del servidor con tarjeta gráfica ni sus llaves de seguridad al público. Si el día de mañana se cambia de proveedor de modelo de lenguaje solo se debe modificar una sola variable de configuración dentro del gateway o del servicio de marketing con la nueva dirección del servidor, sin necesidad de tocar el código de la tienda ni cambiar nada en los clientes.

---

### Pregunta 10, inciso a: Respuesta al inversionista con postura clara y riesgo concreto
Dividir el panel interno a microservicios en una semana con cinco personas es un error peligroso que no aporta valor, porque el panel funciona bien, tiene poco tráfico y no representa ningún problema de lentitud hoy en día. Si forzamos esa separación a ciegas vamos a romper la operación diaria de la empresa, meter fallas de red innecesarias y descuidar la aplicación de los clientes, que es la que verdaderamente genera el dinero. Nuestro compromiso para esta semana es garantizar la estabilidad y seguridad de la aplicación pública de ventas; los microservicios se deben aplicar donde resuelven problemas reales de saturación y no para seguir una moda.

### Pregunta 10, inciso b: Orden de las cuatro iniciativas de más a menos urgente y su justificación
La prioridad número uno es meter autenticación y límite de peticiones en el gateway público porque es la entrada abierta a internet y sin esa protección cualquiera puede tirarnos el sistema o robar datos hoy mismo. La segunda prioridad es sacar el reentrenamiento del modelo a un proceso aparte que no afecte a pedidos, porque actualmente está tirando las compras reales de los clientes cada semana y eso cuesta dinero directamente. La tercera es partir el panel interno de Django, la cual no es urgente porque el panel ya funciona y tiene muy poco tráfico, siendo una tarea que consume mucho tiempo sin dar beneficios inmediatos. La última iniciativa es subir el modelo de lenguaje a producción sin tiempos límite ni plan de respaldo, la cual va al final y no debe hacerse jamás en ese estado porque meter un servicio lento sin protección garantiza la caída del sistema.

### Pregunta 10, inciso c: Métrica observable para decidir cuándo partir una parte del monolito
Una métrica observable muy clara es cuando el tiempo de respuesta de una función específica dentro del monolito supere los tres segundos durante diez minutos seguidos y provoque que el uso de procesador pase del ochenta y cinco por ciento, frenando y haciendo fallar las compras de los demás usuarios en horas pico. Otra métrica de equipo ocurre cuando dos desarrolladores tienen que esperar más de tres días para subir una corrección urgente porque otro equipo está modificando el mismo archivo y bloquea la publicación del sistema.

### Pregunta 10, inciso d: Frase propia de cierre sobre si los microservicios son objetivo o herramienta
Los microservicios son únicamente una herramienta de trabajo para cuando una aplicación crece tanto que ya no cabe de forma organizada en un solo programa, pero nunca deben ser la meta final; si tu negocio funciona rápido y estable en un monolito, partirlo a la fuerza solo te compra problemas y costos que todavía no necesitas.

