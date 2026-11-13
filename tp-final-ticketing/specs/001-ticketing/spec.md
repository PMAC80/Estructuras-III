# Especificación del Sistema de Ticketing

## 1. Metadatos

| Campo | Valor |
|---|---|
| Proyecto | tp-final-ticketing |
| Documento | Especificación del sistema |
| Versión | 1.0 |
| Fecha | 2026-11-09 |
| Estado | Aprobado para implementación |
| Stack | Python 3.10+ / SQLite (sqlite3) / pytest |
| Interfaz | Consola (sin frameworks web) |

## 2. Introducción y objetivo

El Sistema de Ticketing permite a una organización registrar, asignar y dar
seguimiento a tickets de soporte. Los clientes crean tickets asociados a un
producto, los representantes los atienden mediante hitos y mensajes, y el
sistema genera alertas y conserva un historial completo de cada ticket hasta su
cierre o posterior reapertura.

El objetivo es centralizar el ciclo de vida del ticket en una aplicación de
consola en Python puro con persistencia local en SQLite, respetando una
arquitectura estrictamente separada en capas.

## 3. Alcance

### 3.1 Incluido

- Registro y autenticación de usuarios (clientes y representantes).
- Creación de tickets por parte de clientes.
- Asignación de tickets a representantes.
- Comunicación cliente–representante mediante mensajes.
- Gestión de hitos de atención.
- Historial de eventos por ticket.
- Alertas/notificaciones internas por consola.
- Cierre y reapertura de tickets.
- Persistencia en SQLite y pruebas automatizadas con pytest.

### 3.2 Fuera de alcance

- Interfaz web, API REST o cualquier framework web.
- Envío de correos electrónicos o notificaciones push.
- Adjuntos, archivos o imágenes en tickets y mensajes.
- Integraciones con sistemas externos.
- Facturación, reportes analíticos o tableros gráficos.
- Autenticación multifactor o recuperación de contraseña por correo.

## 4. Glosario

| Término | Definición |
|---|---|
| Ticket | Incidente o solicitud de soporte registrada por un cliente. |
| Hito | Etapa o entregable planificado dentro de la atención de un ticket. |
| Mensaje | Comunicación escrita entre el cliente y el representante dentro de un ticket. |
| Representante | Usuario encargado de atender y resolver tickets. |
| Cliente | Usuario que reporta incidentes y da seguimiento a sus tickets. |
| Alerta | Aviso interno generado por el sistema ante eventos relevantes. |
| Historial | Registro cronológico e inmutable de los eventos de un ticket. |
| TipoProducto | Categoría a la que pertenece un producto. |
| Producto | Bien o servicio sobre el cual se reporta un ticket. |

## 5. Actores y roles

| Actor | Rol | Descripción |
|---|---|---|
| Usuario | Base | Entidad común con credenciales y datos de identidad. |
| Cliente | Usuario | Crea tickets, consulta su estado, comunica y solicita reapertura. |
| Representante | Usuario | Recibe asignaciones, gestiona hitos, responde mensajes, cierra tickets. |
| Sistema | Automático | Genera alertas, registra historial y valida reglas de estado. |

### 5.1 Herencia de roles

- `Cliente` hereda de `Usuario`.
- `Representante` hereda de `Usuario`.
- Un usuario posee exactamente un rol activo: `CLIENTE` o `REPRESENTANTE`.
- Las operaciones sensibles validan el rol antes de ejecutarse.

## 6. Requisitos funcionales (RF1–RF10)

Convenciones: prioridad `Alta` / `Media` / `Baja`; el criterio de aceptación debe
poder verificarse con al menos un test automatizado.

### RF1 — Registro de usuarios

- **Descripción:** permitir el alta de clientes y representantes con datos
  válidos y credenciales seguras.
- **Actor:** Usuario no registrado.
- **Entradas:** nombre, email, contraseña, rol, datos opcionales del rol
  (empresa/teléfono para cliente; legajo/especialidad para representante).
- **Salidas:** usuario persistido con identificador único; mensaje de éxito.
- **Reglas:**
  - El email debe ser único y tener formato válido.
  - La contraseña debe almacenarse hasheada con salt; nunca en texto plano.
  - El rol debe ser `CLIENTE` o `REPRESENTANTE`.
  - Los campos obligatorios no pueden estar vacíos.
- **Criterios de aceptación:**
  - Un registro válido crea el usuario y permite iniciar sesión.
  - Un email duplicado es rechazado con mensaje claro.
  - La contraseña no se recupera en texto plano desde la base de datos.
- **Prioridad:** Alta.

### RF2 — Login y sesión

- **Descripción:** autenticar a un usuario registrado y habilitar su menú según
  el rol.
- **Actor:** Usuario registrado.
- **Entradas:** email y contraseña.
- **Salidas:** sesión activa con rol e identidad del usuario; menú
  correspondiente.
- **Reglas:**
  - Credenciales inválidas no revelan qué dato es incorrecto.
  - Un usuario inactivo no puede iniciar sesión.
  - La sesión se cierra explícitamente con la opción "Cerrar sesión".
- **Criterios de aceptación:**
  - Credenciales correctas inician sesión y muestran el menú del rol.
  - Credenciales incorrectas muestran error y no crean sesión.
  - Tras cerrar sesión, las operaciones requieren autenticarse nuevamente.
- **Prioridad:** Alta.

### RF3 — Crear ticket

- **Descripción:** permitir que un cliente registre un ticket asociado a un
  producto y tipo de producto.
- **Actor:** Cliente autenticado.
- **Entradas:** título, descripción, prioridad, producto, tipo de producto,
  fecha de creación.
- **Salidas:** ticket persistido en estado `NUEVO` con identificador único.
- **Reglas:**
  - Título y descripción son obligatorios.
  - El producto debe existir y pertenecer al tipo de producto indicado.
  - La prioridad debe ser `BAJA`, `MEDIA` o `ALTA`.
  - El cliente se toma de la sesión activa, no se ingresa manualmente.
- **Criterios de aceptación:**
  - Un ticket válido se guarda con estado `NUEVO` y cliente correcto.
  - Datos obligatorios faltantes impiden la creación con mensaje claro.
  - Todo ticket creado genera un evento en el historial.
- **Prioridad:** Alta.

### RF4 — Asignar ticket

- **Descripción:** asignar un ticket `NUEVO` a un representante.
- **Actor:** Representante autenticado o usuario con permiso de asignación.
- **Entradas:** identificador de ticket, identificador de representante.
- **Salidas:** ticket actualizado a estado `ASIGNADO` con representante
  asignado.
- **Reglas:**
  - Solo se asignan tickets en estado `NUEVO` o `REABIERTO`.
  - El representante debe existir y estar activo.
  - No se puede asignar un ticket `CERRADO`.
  - La asignación registra historial y genera una alerta al representante.
- **Criterios de aceptación:**
  - Asignar un ticket `NUEVO` cambia su estado a `ASIGNADO`.
  - Asignar a un representante inexistente o inactivo es rechazado.
  - La operación queda registrada en el historial con actor y fecha.
- **Prioridad:** Alta.

### RF5 — Comunicación (mensajes)

- **Descripción:** permitir el intercambio de mensajes entre cliente y
  representante dentro de un ticket.
- **Actor:** Cliente o Representante autenticado con acceso al ticket.
- **Entradas:** identificador de ticket, contenido del mensaje, autor.
- **Salidas:** mensaje persistido con fecha, autor y estado de lectura.
- **Reglas:**
  - El contenido no puede estar vacío.
  - Solo participan el cliente dueño del ticket y el representante asignado.
  - No se permiten mensajes en tickets `CERRADO` salvo reapertura previa.
  - Cada mensaje registra historial y puede generar alerta al destinatario.
- **Criterios de aceptación:**
  - Un mensaje válido se guarda y es visible para ambas partes.
  - Un usuario ajeno al ticket no puede enviar mensajes.
  - El mensaje aparece en el historial con fecha y autor.
- **Prioridad:** Alta.

### RF6 — Hitos

- **Descripción:** gestionar hitos de atención dentro de un ticket para
  planificar y controlar el avance.
- **Actor:** Representante asignado.
- **Entradas:** identificador de ticket, descripción, fecha compromiso, orden.
- **Salidas:** hito persistido con estado `PENDIENTE`, `EN_PROGRESO`,
  `CUMPLIDO` o `VENCIDO`.
- **Reglas:**
  - Un hito pertenece a un único ticket.
  - La fecha compromiso no puede ser anterior a la fecha de creación del ticket.
  - Al completar el último hito, el ticket puede pasar a `RESUELTO`.
  - Los hitos vencidos generan alerta automática.
- **Criterios de aceptación:**
  - Crear y actualizar hitos refleja el estado correcto.
  - Completar todos los hitos habilita la resolución del ticket.
  - Un hito con fecha vencida es reportado por `ControlHito`.
- **Prioridad:** Media.

### RF7 — Historial

- **Descripción:** registrar cronológicamente todos los eventos relevantes de
  un ticket.
- **Actor:** Sistema (automático).
- **Entradas:** ticket, actor, tipo de evento, estado anterior, estado nuevo,
  detalle, fecha.
- **Salidas:** entradas de historial inmutables consultables por ticket.
- **Reglas:**
  - Se registran al menos: creación, asignación, cambio de estado, mensaje,
    hito y cierre/reapertura.
  - Las entradas no se modifican ni eliminan.
  - El historial se ordena por fecha ascendente.
- **Criterios de aceptación:**
  - Cada operación relevante produce exactamente una entrada de historial.
  - La consulta del historial devuelve los eventos en orden cronológico.
  - El historial no puede alterarse desde la interfaz.
- **Prioridad:** Alta.

### RF8 — Alertas y notificaciones

- **Descripción:** generar y consultar alertas internas ante eventos que
  requieren atención.
- **Actor:** Sistema (generación); Representante (consulta).
- **Entradas:** eventos del sistema (ticket sin asignar, hito vencido, mensaje
  nuevo, cambio de estado).
- **Salidas:** alertas persistidas con tipo, prioridad, fecha y estado
  `PENDIENTE`/`LEIDA`.
- **Reglas:**
  - Un ticket `NUEVO` sin asignar por más de 24 horas genera alerta.
  - Un hito con fecha compromiso vencida genera alerta.
  - Un mensaje nuevo genera alerta al destinatario.
  - Las alertas pueden marcarse como leídas.
- **Criterios de aceptación:**
  - Los escenarios anteriores generan la alerta correspondiente.
  - `ControlNotificaciones` lista solo las alertas del usuario o rol
    destinatario.
  - Marcar una alerta como leída no la elimina.
- **Prioridad:** Media.

### RF9 — Cierre de ticket

- **Descripción:** cerrar un ticket cuando la atención haya finalizado.
- **Actor:** Representante asignado.
- **Entradas:** identificador de ticket, comentario de cierre.
- **Salidas:** ticket en estado `CERRADO` con fecha de cierre.
- **Reglas:**
  - Solo se cierran tickets en estado `RESUELTO`.
  - Deben existir hitos y todos deben estar `CUMPLIDO` o justificarse el cierre.
  - Un ticket `CERRADO` es de solo lectura para mensajes e hitos.
  - El cierre registra historial y genera alerta al cliente.
- **Criterios de aceptación:**
  - Cerrar un ticket `RESUELTO` con hitos cumplidos actualiza estado y fecha.
  - Intentar cerrar un ticket no `RESUELTO` es rechazado.
  - Tras el cierre, no se aceptan mensajes ni hitos nuevos.
- **Prioridad:** Alta.

### RF10 — Reapertura de ticket

- **Descripción:** reabrir un ticket cerrado cuando el problema persiste o
  reaparece.
- **Actor:** Cliente dueño del ticket o Representante autorizado.
- **Entradas:** identificador de ticket, motivo de reapertura.
- **Salidas:** ticket en estado `REABIERTO` y luego `ASIGNADO`.
- **Reglas:**
  - Solo se reabren tickets en estado `CERRADO`.
  - El motivo de reapertura es obligatorio.
  - Se registra historial con motivo, actor y fecha.
  - La reapertura genera alerta al representante asignado o al equipo.
- **Criterios de aceptación:**
  - Reabrir un ticket `CERRADO` lo pasa a `REABIERTO` y permite nueva
    asignación.
  - Reabrir sin motivo es rechazado.
  - La operación queda reflejada en el historial y genera alerta.
- **Prioridad:** Media.

## 7. Requisitos no funcionales (RNF)

| ID | Requisito | Criterio |
|---|---|---|
| RNF1 | Persistencia | Toda entidad se almacena en SQLite mediante la capa `db`. |
| RNF2 | Seguridad | Contraseñas hasheadas con salt; nunca en texto plano. |
| RNF3 | Integridad | Claves foráneas e integridad referencial activas en SQLite. |
| RNF4 | Trazabilidad | Toda operación relevante queda en el historial. |
| RNF5 | Usabilidad | Interfaz de consola clara, mensajes y menús en español. |
| RNF6 | Rendimiento | Operaciones locales responden en menos de 1 segundo. |
| RNF7 | Portabilidad | Python 3.10+ en Windows, Linux o macOS. |
| RNF8 | Testabilidad | TDD con pytest; no se avanza con tests en rojo. |
| RNF9 | Mantenibilidad | Separación estricta en capas `models`, `db`, `controller`, `gui`. |
| RNF10 | Nomenclatura | Clases en PascalCase; métodos en camelCase. |

## 8. Casos de uso

### C-1 — Login

| Campo | Detalle |
|---|---|
| Actores | Usuario registrado |
| Precondiciones | El usuario existe y está activo. |
| Postcondiciones | Sesión activa con rol e identidad; acceso al menú correspondiente. |
| RF asociados | RF2 |

**Flujo principal**
1. El usuario selecciona "Iniciar sesión".
2. El sistema solicita email y contraseña.
3. El usuario ingresa las credenciales.
4. El sistema valida formato y busca al usuario por email.
5. El sistema verifica el hash de la contraseña.
6. El sistema crea la sesión y muestra el menú según el rol.
7. El caso de uso finaliza con éxito.

**Flujos alternativos**
- **A1 — Credenciales inválidas:** el sistema muestra un error genérico y
  permite reintentar.
- **A2 — Usuario inactivo:** el sistema rechaza el acceso indicando que la
  cuenta no está habilitada.
- **A3 — Campos vacíos:** el sistema solicita completar los datos obligatorios.

### C-2 — Crear Ticket

| Campo | Detalle |
|---|---|
| Actores | Cliente autenticado |
| Precondiciones | Sesión activa con rol `CLIENTE`; existe al menos un tipo de producto y un producto. |
| Postcondiciones | Ticket persistido en estado `NUEVO`; historial registrado. |
| RF asociados | RF3, RF7 (historial), RF8 (alerta si corresponde) |

**Flujo principal**
1. El cliente elige "Crear ticket".
2. El sistema lista los tipos de producto.
3. El cliente selecciona un tipo de producto y luego un producto.
4. El sistema solicita título, descripción y prioridad.
5. El cliente completa los datos y confirma.
6. El sistema valida campos, producto y prioridad.
7. El sistema crea el ticket en estado `NUEVO` asociado al cliente de la sesión.
8. El sistema registra el evento de creación en el historial.
9. El sistema muestra el identificador del ticket creado.
10. El caso de uso finaliza con éxito.

**Flujos alternativos**
- **A1 — Campos obligatorios vacíos:** el sistema muestra error y solicita
  corregirlos.
- **A2 — Producto/tipo inválido:** el sistema rechaza la creación y muestra un
  mensaje claro.
- **A3 — Sin tipos de producto:** el sistema informa que no es posible crear
  tickets hasta que existan datos maestros.

### C-3 — Revisar Alertas

| Campo | Detalle |
|---|---|
| Actores | Representante autenticado |
| Precondiciones | Sesión activa con rol `REPRESENTANTE`. |
| Postcondiciones | Alertas listadas; las seleccionadas quedan marcadas como leídas. |
| RF asociados | RF8, RF7 (historial si se navega al ticket) |

**Flujo principal**
1. El representante elige "Revisar alertas".
2. El sistema consulta las alertas pendientes del usuario o su rol.
3. El sistema muestra tipo, prioridad, fecha y referencia al ticket.
4. El representante selecciona una alerta.
5. El sistema muestra el detalle y permite abrir el ticket asociado.
6. El sistema marca la alerta como leída.
7. El caso de uso finaliza con éxito.

**Flujos alternativos**
- **A1 — Sin alertas:** el sistema informa "No hay alertas pendientes".
- **A2 — Ticket asociado inexistente:** el sistema muestra la alerta sin
  permitir navegación y registra la inconsistencia.
- **A3 — Alerta ya leída:** el sistema la muestra como leída y no la vuelve a
  marcar.

## 9. Modelo de clases UML

### 9.1 Capa `models` (entidades puras)

| Clase | Atributos principales | Métodos (camelCase) | Relaciones |
|---|---|---|---|
| `Usuario` | `idUsuario`, `nombre`, `email`, `contrasenaHash`, `rol`, `activo` | `iniciarSesion()`, `cerrarSesion()`, `cambiarContrasena()`, `esRepresentante()`, `esCliente()` | Base de `Cliente` y `Representante`. |
| `Cliente` | `empresa`, `telefono` | `crearTicket()`, `reabrirTicket()`, `verHistorial()` | Hereda de `Usuario`; 1..* `Ticket`. |
| `Representante` | `legajo`, `especialidad` | `asignarTicket()`, `responderMensaje()`, `actualizarHito()`, `cerrarTicket()` | Hereda de `Usuario`; 0..* `Ticket` asignados. |
| `Ticket` | `idTicket`, `titulo`, `descripcion`, `estado`, `prioridad`, `fechaCreacion`, `fechaCierre`, `idCliente`, `idRepresentante`, `idProducto`, `idTipoProducto` | `asignar()`, `cambiarEstado()`, `cerrar()`, `reabrir()`, `agregarMensaje()`, `agregarHito()` | 1 `Cliente`; 0..1 `Representante`; 1 `Producto`; 1..* `Hito`; 1..* `Mensaje`. |
| `Hito` | `idHito`, `idTicket`, `descripcion`, `fechaCompromiso`, `fechaCumplimiento`, `estado`, `orden` | `completar()`, `actualizarEstado()`, `estaVencido()` | * a 1 `Ticket`. |
| `Mensaje` | `idMensaje`, `idTicket`, `idAutor`, `contenido`, `fechaEnvio`, `leido` | `marcarLeido()`, `esDeCliente()` | * a 1 `Ticket`; 1 `Usuario` autor. |
| `Producto` | `idProducto`, `nombre`, `version`, `idTipoProducto` | `getDescripcion()`, `perteneceA()` | * a 1 `TipoProducto`; 1..* `Ticket`. |
| `TipoProducto` | `idTipoProducto`, `nombre`, `descripcion` | `listarProductos()` | 1..* `Producto`. |

### 9.2 Capa `controller` (lógica)

| Clase | Responsabilidad | Métodos (camelCase) |
|---|---|---|
| `ControlTicket` | Alta, asignación, cambios de estado, cierre, reapertura, mensajes y consulta de historial. | `crearTicket()`, `asignarTicket()`, `cambiarEstado()`, `cerrarTicket()`, `reabrirTicket()`, `agregarMensaje()`, `listarTickets()`, `obtenerHistorial()`, `registrarHistorial()` |
| `ControlHito` | Gestión de hitos y detección de vencimientos. | `crearHito()`, `actualizarHito()`, `completarHito()`, `listarHitos()`, `verificarVencidos()` |
| `ControlNotificaciones` | Generación, consulta y marcado de alertas. | `generarAlerta()`, `listarAlertas()`, `marcarLeida()`, `notificarCambioEstado()`, `notificarMensaje()` |

### 9.3 Capa `gui` (interfaz por consola)

| Clase | Responsabilidad | Métodos (camelCase) |
|---|---|---|
| `GUI` | Mostrar menús, capturar entradas, invocar controladores y presentar resultados. | `iniciar()`, `mostrarMenu()`, `ejecutarLogin()`, `ejecutarRegistro()`, `ejecutarCrearTicket()`, `ejecutarAsignarTicket()`, `ejecutarRevisarAlertas()`, `ejecutarGestionHitos()`, `ejecutarCerrarTicket()`, `ejecutarReabrirTicket()`, `cerrarSesion()` |

### 9.4 Estructuras internas de persistencia no UML

Para respetar el UML provisto no se agregan clases de dominio adicionales:

- **Historial:** registro interno gestionado por `ControlTicket` y persistido por
  la capa `db` (RF7).
- **Alerta:** registro interno gestionado por `ControlNotificaciones` y
  persistido por la capa `db` (RF8).

## 10. Arquitectura por capas

| Capa | Paquete | Contenido | Dependencias permitidas |
|---|---|---|---|
| Modelos | `src/models/` | Entidades puras y reglas de estado básicas. | Ninguna. |
| Persistencia | `src/db/` | Acceso a SQLite, repositorios y mapeo. | `models`. |
| Controladores | `src/controller/` | Casos de uso y reglas de negocio. | `models`, `db`. |
| Interfaz | `src/gui/` | Menús y entrada/salida por consola. | `controller`, `models`. |

Reglas de dependencia:

- `gui` no accede directamente a `db`.
- `models` no conoce `db`, `controller` ni `gui`.
- Los controladores coordinan la persistencia y devuelven resultados o errores
  de negocio.
- Toda comunicación con SQLite ocurre en `db`.

## 11. Modelo de datos SQLite (nivel especificación)

Convención: tablas y columnas en `snake_case`; la conversión a camelCase ocurre
en la capa de mapeo.

### 11.1 Tablas

| Tabla | Columnas principales | Restricciones |
|---|---|---|
| `usuario` | `id_usuario` (PK), `nombre`, `email` (UNIQUE), `contrasena_hash`, `rol`, `activo` | `rol` en (`CLIENTE`, `REPRESENTANTE`); `activo` booleano. |
| `cliente` | `id_usuario` (PK/FK → `usuario`), `empresa`, `telefono` | Herencia por tabla auxiliar. |
| `representante` | `id_usuario` (PK/FK → `usuario`), `legajo` (UNIQUE), `especialidad` | Herencia por tabla auxiliar. |
| `tipo_producto` | `id_tipo_producto` (PK), `nombre` (UNIQUE), `descripcion` | — |
| `producto` | `id_producto` (PK), `nombre`, `version`, `id_tipo_producto` (FK) | FK → `tipo_producto`. |
| `ticket` | `id_ticket` (PK), `titulo`, `descripcion`, `estado`, `prioridad`, `fecha_creacion`, `fecha_cierre`, `id_cliente` (FK), `id_representante` (FK), `id_producto` (FK), `id_tipo_producto` (FK) | `estado` y `prioridad` restringidos; FKs obligatorias salvo `id_representante`. |
| `hito` | `id_hito` (PK), `id_ticket` (FK), `descripcion`, `fecha_compromiso`, `fecha_cumplimiento`, `estado`, `orden` | FK → `ticket`; `estado` restringido. |
| `mensaje` | `id_mensaje` (PK), `id_ticket` (FK), `id_autor` (FK), `contenido`, `fecha_envio`, `leido` | FKs → `ticket`, `usuario`. |
| `historial` | `id_evento` (PK), `id_ticket` (FK), `id_actor` (FK), `tipo_evento`, `estado_anterior`, `estado_nuevo`, `detalle`, `fecha` | Solo inserción; sin actualización ni borrado. |
| `alerta` | `id_alerta` (PK), `id_usuario` (FK), `id_ticket` (FK), `tipo`, `prioridad`, `mensaje`, `estado`, `fecha_creacion` | `estado` en (`PENDIENTE`, `LEIDA`). |

### 11.2 Reglas de integridad

- Claves foráneas activas (`PRAGMA foreign_keys = ON`).
- Borrado restringido: no se eliminan tickets con hitos, mensajes o historial.
- `email` y `legajo` son únicos.
- `fecha_cierre` solo se completa al pasar a `CERRADO`.
- Toda escritura de estado en `ticket` genera una fila en `historial`.

## 12. Máquina de estados del Ticket

### 12.1 Estados

| Estado | Descripción |
|---|---|
| `NUEVO` | Ticket creado por el cliente, sin representante asignado. |
| `ASIGNADO` | Ticket asignado a un representante. |
| `EN_PROGRESO` | Representante trabajando activamente en el ticket. |
| `RESUELTO` | Atención finalizada, pendiente de cierre formal. |
| `CERRADO` | Ticket cerrado; solo lectura salvo reapertura. |
| `REABIERTO` | Ticket cerrado que volvió a abrirse por un motivo. |

### 12.2 Transiciones

| Desde | Evento | Hacia | Actor | Regla |
|---|---|---|---|---|
| `NUEVO` | Asignar representante | `ASIGNADO` | Representante | RF4 |
| `ASIGNADO` | Iniciar atención | `EN_PROGRESO` | Representante | — |
| `EN_PROGRESO` | Completar último hito | `RESUELTO` | Representante | RF6 |
| `EN_PROGRESO` | Resolver manualmente | `RESUELTO` | Representante | — |
| `RESUELTO` | Cerrar ticket | `CERRADO` | Representante | RF9 |
| `CERRADO` | Reabrir con motivo | `REABIERTO` | Cliente/Representante | RF10 |
| `REABIERTO` | Asignar representante | `ASIGNADO` | Representante | RF4 |

### 12.3 Transiciones prohibidas

- `NUEVO` → `CERRADO` (debe asignarse y resolverse antes).
- `CERRADO` → `EN_PROGRESO` (requiere reapertura y asignación).
- Cualquier transición desde `CERRADO` distinta de `REABIERTO`.
- `RESUELTO` → `EN_PROGRESO` sin justificación registrada.

## 13. Matriz de trazabilidad

| RF | Caso de uso | Clases de modelo | Controlador | Capa GUI | Persistencia |
|---|---|---|---|---|---|
| RF1 Registro | — (transversal) | `Usuario`, `Cliente`, `Representante` | — (validación en `models`/`db`) | `ejecutarRegistro()` | `usuario`, `cliente`, `representante` |
| RF2 Login | C-1 | `Usuario` | — (autenticación) | `ejecutarLogin()` | `usuario` |
| RF3 Crear ticket | C-2 | `Ticket`, `Cliente`, `Producto`, `TipoProducto` | `ControlTicket.crearTicket()` | `ejecutarCrearTicket()` | `ticket`, `historial` |
| RF4 Asignar ticket | — | `Ticket`, `Representante` | `ControlTicket.asignarTicket()` | `ejecutarAsignarTicket()` | `ticket`, `historial`, `alerta` |
| RF5 Comunicación | — | `Mensaje`, `Ticket`, `Usuario` | `ControlTicket.agregarMensaje()` | Menú de mensajes | `mensaje`, `historial`, `alerta` |
| RF6 Hitos | — | `Hito`, `Ticket` | `ControlHito.crearHito()`, `actualizarHito()`, `completarHito()` | `ejecutarGestionHitos()` | `hito`, `historial` |
| RF7 Historial | C-2 / C-3 (navegación) | `Ticket` (consulta) | `ControlTicket.obtenerHistorial()`, `registrarHistorial()` | Menú de historial | `historial` |
| RF8 Alertas | C-3 | `Usuario`, `Ticket` | `ControlNotificaciones.listarAlertas()`, `generarAlerta()` | `ejecutarRevisarAlertas()` | `alerta` |
| RF9 Cierre | — | `Ticket`, `Hito` | `ControlTicket.cerrarTicket()` | `ejecutarCerrarTicket()` | `ticket`, `historial`, `alerta` |
| RF10 Reapertura | — | `Ticket`, `Cliente`, `Representante` | `ControlTicket.reabrirTicket()` | `ejecutarReabrirTicket()` | `ticket`, `historial`, `alerta` |

## 14. Supuestos y decisiones pendientes

### 14.1 Supuestos adoptados

1. `Cliente` y `Representante` heredan de `Usuario`.
2. Las contraseñas se almacenan hasheadas con salt; nunca en texto plano.
3. Cada ticket pertenece a un cliente, referencia un producto y su tipo, y se
   asigna como máximo a un representante a la vez.
4. Las alertas son internas y se muestran por consola; no se envían correos.
5. El historial es una bitácora inmutable de eventos del ticket.
6. Cierre y reapertura están restringidos por rol y por estado del ticket.
7. La interfaz es de consola y en español; los mensajes de error son claros y
   no exponen datos sensibles.
8. Los datos maestros (`TipoProducto`, `Producto`) se cargan previamente; la
   spec no define su mantenimiento por GUI.

### 14.2 Decisiones pendientes de confirmar antes de implementar

1. Regla exacta de bloqueo por intentos fallidos de login.
2. Plazo configurable de alerta para tickets sin asignar (propuesto: 24 h).
3. Permisos exactos para que un representante reabra tickets de otro
   representante.
4. Política de cierre con hitos pendientes (¿prohibido o permitido con
   justificación?).
5. Existencia de un rol administrador para la carga de datos maestros.

## 15. Criterios de aceptación globales

- Todos los RF cuentan con al menos un test automatizado en pytest.
- La aplicación inicia desde consola, permite registro, login y operación según
  rol.
- Toda transición de estado respeta la máquina de estados de la sección 12.
- Toda operación relevante queda registrada en el historial.
- Los datos persisten entre ejecuciones en SQLite.
- No existen dependencias de frameworks web.
- La nomenclatura respeta PascalCase para clases y camelCase para métodos.
