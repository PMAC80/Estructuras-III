# Tareas de Implementación — Sistema de Ticketing

Referencias: `specs/001-ticketing/spec.md` y `specs/001-ticketing/plan.md`.

## Convenciones

- Cada tarea está pensada para **20–30 minutos**.
- Formato: `[ ] TNNN — descripción (RF/CU) · estimación`.
- **Hecho cuando:** criterio verificable, no una intención.
- Regla de oro: primero el test en rojo, luego la implementación mínima en verde.
- No se avanza a la tarea siguiente si la suite de pytest está en rojo.
- No se escribe código de una tarea sin haber escrito antes su test.
- Las tareas se ejecutan en orden salvo que se indique una dependencia distinta.

## Fase 0 — Preparación

- [x] **T001 — Crear estructura de paquetes y archivos base** · 30 min
  - Crear `src/models/`, `src/db/`, `src/db/repositorios/`,
    `src/controller/`, `src/gui/`, `tests/unit/`, `tests/integration/`,
    `tests/e2e/`, con sus `__init__.py`.
  - **Hecho cuando:** `python -c "import src"` funciona y pytest descubre
    `tests/` sin errores de importación.

- [x] **T002 — Configurar pytest y metadatos del proyecto** · 20 min
  - Crear `pyproject.toml` con configuración de pytest y sin dependencias
    externas de runtime.
  - **Hecho cuando:** `pytest -q` se ejecuta y reporta 0 tests fallidos (aún sin
    tests implementados).

- [x] **T003 — Definir configuración de la base de datos** · 20 min
  - Implementar resolución de ruta por `TICKETING_DB_PATH` con valor por
    defecto `ticketing.db`, usando `pathlib`.
  - **Hecho cuando:** un test verifica la ruta por defecto y la ruta por
    variable de entorno.

- [x] **T004 — Definir excepciones de dominio** · 25 min
  - Crear `ErrorDominio`, `ErrorValidacion`, `ErrorAutenticacion`,
    `ErrorPermiso`, `ErrorEstado`, `ErrorNoEncontrado`, `ErrorConflicto`.
  - **Hecho cuando:** un test verifica la jerarquía y que los mensajes están en
    español.

## Fase 1 — Modelos puros

- [x] **T005 — Implementar seguridad de contraseñas (RF1, RF2)** · 30 min
  - Hash PBKDF2-HMAC-SHA256 con salt y verificación en tiempo constante.
  - **Hecho cuando:** pasan los tests de hash distinto por salt, verificación
    correcta, rechazo de contraseña incorrecta y formato almacenado sin texto
    plano.

- [x] **T006 — Implementar `Usuario` (RF1, RF2)** · 30 min
  - Atributos, normalización de email, rol válido, estado activo por defecto y
    contraseña hasheada.
  - **Hecho cuando:** tests de creación válida, email inválido, rol inválido y
    ausencia de contraseña en texto plano pasan.

- [x] **T007 — Implementar `Cliente` y `Representante` (RF1)** · 25 min
  - Herencia desde `Usuario` y validaciones propias (`empresa`/`telefono`,
    `legajo`/`especialidad`).
  - **Hecho cuando:** tests de herencia, datos obligatorios y legajo válido
    pasan.

- [x] **T008 — Implementar `TipoProducto` y `Producto` (RF3)** · 25 min
  - Validar nombre no vacío y pertenencia de producto a tipo.
  - **Hecho cuando:** tests de creación y de producto con tipo inválido pasan.

- [x] **T009 — Implementar creación y validación de `Ticket` (RF3)** · 30 min
  - Estado inicial `NUEVO`, prioridad válida, campos obligatorios y cliente
    asociado.
  - **Hecho cuando:** tests de ticket válido, prioridad inválida y campos
    faltantes pasan.

- [x] **T010 — Implementar máquina de estados del `Ticket` (RF4, RF9, RF10)** · 30 min
  - Constantes de estado/evento y tabla de transiciones permitidas; rechazo de
    transiciones prohibidas.
  - **Hecho cuando:** tests cubren todas las transiciones de §12 de `spec.md` y
    al menos una prohibida por cada estado.

- [x] **T011 — Implementar `Hito` (RF6)** · 25 min
  - Estados, fecha compromiso, cumplimiento y cálculo de vencimiento.
  - **Hecho cuando:** tests de creación, transición de estado y `estaVencido()`
    pasan con reloj fijo.

- [x] **T012 — Implementar `Mensaje` (RF5)** · 20 min
  - Contenido obligatorio, autor, fecha y estado de lectura.
  - **Hecho cuando:** tests de mensaje válido, contenido vacío y marcado como
    leído pasan.

## Fase 2 — Persistencia

- [x] **T013 — Implementar conexión SQLite (RF7, RNF1, RNF3)** · 25 min
  - Apertura/cierre con context manager, `row_factory`, `PRAGMA
    foreign_keys = ON`.
  - **Hecho cuando:** tests verifican conexión a DB temporal, cierre correcto y
    claves foráneas activas.

- [x] **T014 — Implementar esquema de base de datos (RNF1, RNF3)** · 30 min
  - Tablas, restricciones e índices según §11 de `spec.md`, creación
    idempotente.
  - **Hecho cuando:** tests verifican existencia de las 10 tablas, `CHECK` de
    estados/prioridades/roles y ejecución doble sin errores.

- [x] **T015 — Implementar mapeo fila ↔ entidad** · 25 min
  - Conversión `snake_case` ↔ `camelCase` para todas las entidades.
  - **Hecho cuando:** tests de ida y vuelta para cada entidad pasan sin pérdida
    de datos.

- [x] **T016 — Implementar `RepositorioUsuario` (RF1, RF2)** · 30 min
  - Insertar, buscar por email/id, listar activos e inactivos, unicidad de
    email.
  - **Hecho cuando:** tests de alta, búsqueda, email duplicado y usuario
    inactivo pasan.

- [x] **T017 — Implementar repositorios de `Cliente` y `Representante` (RF1)** · 30 min
  - Alta y búsqueda por id de usuario, unicidad de legajo.
  - **Hecho cuando:** tests de alta, búsqueda y legajo duplicado pasan.

- [x] **T018 — Implementar repositorios de `TipoProducto` y `Producto` (RF3)** · 25 min
  - Alta, listado, búsqueda por id y listado por tipo.
  - **Hecho cuando:** tests de CRUD y filtrado por tipo pasan.

- [x] **T019 — Implementar `RepositorioTicket` (RF3, RF4, RF9, RF10)** · 30 min
  - Insertar, buscar, listar por cliente/representante/estado, actualizar
    estado y asignación, listar sin asignar.
  - **Hecho cuando:** tests de alta, consultas, actualización de estado y
    asignación pasan.

- [x] **T020 — Implementar `RepositorioHito` (RF6)** · 25 min
  - Insertar, buscar, listar por ticket, actualizar y listar vencidos.
  - **Hecho cuando:** tests de alta, actualización, orden y vencidos pasan.

- [x] **T021 — Implementar `RepositorioMensaje` (RF5)** · 25 min
  - Insertar, listar por ticket en orden cronológico y marcar leído.
  - **Hecho cuando:** tests de alta, orden, marcado de lectura y filtrado por
    ticket pasan.

- [x] **T022 — Implementar `RepositorioHistorial` (RF7)** · 20 min
  - Insertar y listar por ticket en orden ascendente, sin actualización ni
    borrado.
  - **Hecho cuando:** tests verifican orden cronológico y ausencia de métodos de
    modificación.

- [x] **T023 — Implementar `RepositorioAlerta` (RF8)** · 25 min
  - Insertar, listar por usuario/rol, listar pendientes y marcar leída.
  - **Hecho cuando:** tests de alta, filtrado por destinatario, pendientes y
    marcado como leída pasan.

- [x] **T024 — Implementar transacciones y rollback (RNF3, RF7)** · 30 min
  - Agrupar escrituras de ticket + historial + alerta y revertir ante error.
  - **Hecho cuando:** un test fuerza un fallo intermedio y verifica que no queda
    ningún registro parcial.

- [x] **T025 — Implementar carga de datos iniciales** · 25 min
  - Tipos de producto y productos base de forma idempotente.
  - **Hecho cuando:** ejecutar la carga dos veces no duplica registros y los
    productos quedan asociados a su tipo.

## Fase 3 — Controladores

- [x] **T026 — Implementar registro en `ControlUsuario` (RF1)** · 30 min
  - Validación de datos, rol, email único y contraseña hasheada.
  - **Hecho cuando:** tests de registro válido, email duplicado, rol inválido y
    contraseña insegura pasan.

- [x] **T027 — Implementar login y sesión en `ControlUsuario` (RF2, C-1)** · 30 min
  - Verificación de credenciales, usuario activo y creación de `Sesion`.
  - **Hecho cuando:** tests de login válido, credenciales inválidas, usuario
    inactivo y datos de sesión correctos pasan.

- [x] **T028 — Implementar logout y verificación de permisos (RF2)** · 20 min
  - Cierre de sesión y helper de autorización por rol.
  - **Hecho cuando:** tests verifican que tras logout no hay sesión y que un rol
    sin permiso recibe `ErrorPermiso`.

- [x] **T029 — Implementar creación de tickets en `ControlTicket` (RF3, C-2)** · 30 min
  - Validaciones, estado `NUEVO`, asociación al cliente de la sesión y registro
    de historial.
  - **Hecho cuando:** tests de alta válida, datos inválidos, cliente de sesión y
    evento de historial pasan.

- [x] **T030 — Implementar asignación en `ControlTicket` (RF4)** · 30 min
  - Validar estado y representante activo; actualizar ticket, historial y
    alerta.
  - **Hecho cuando:** tests de asignación válida, representante inactivo,
    estado inválido y alerta generada pasan.

- [x] **T031 — Implementar cambios de estado en `ControlTicket` (RF4, RF6, RF9)** · 25 min
  - Aplicar la tabla de transiciones y persistir el cambio con historial.
  - **Hecho cuando:** tests de transición permitida y prohibida pasan y el
    estado persistido coincide con el esperado.

- [x] **T032 — Implementar mensajes en `ControlTicket` (RF5)** · 30 min
  - Validar pertenencia al ticket, contenido y estado no cerrado; persistir
    mensaje, historial y alerta.
  - **Hecho cuando:** tests de mensaje válido, usuario ajeno, ticket cerrado y
    alerta al destinatario pasan.

- [x] **T033 — Implementar consultas de tickets e historial (RF3, RF7)** · 25 min
  - Listar tickets por cliente/representante y obtener historial ordenado.
  - **Hecho cuando:** tests verifican filtrado por rol y orden cronológico del
    historial.

- [x] **T034 — Implementar hitos en `ControlHito` (RF6)** · 30 min
  - Crear, actualizar y completar hitos; al completar el último, resolver el
    ticket.
  - **Hecho cuando:** tests de alta, actualización, completado y resolución
    automática del ticket pasan.

- [x] **T035 — Implementar detección de hitos vencidos (RF6, RF8)** · 25 min
  - Detectar vencidos con reloj inyectable y generar alerta.
  - **Hecho cuando:** tests con reloj fijo verifican vencidos y alerta
    generada.

- [x] **T036 — Implementar cierre de tickets (RF9)** · 30 min
  - Exigir estado `RESUELTO`, hitos cumplidos o justificación; persistir estado,
    fecha, historial y alerta.
  - **Hecho cuando:** tests de cierre válido, estado inválido, hitos pendientes
    y bloqueo de mensajes/hitos posteriores pasan.

- [x] **T037 — Implementar reapertura de tickets (RF10)** · 30 min
  - Exigir estado `CERRADO` y motivo; persistir `REABIERTO`, historial y
    alerta.
  - **Hecho cuando:** tests de reapertura válida, sin motivo, estado inválido y
    alerta generada pasan.

- [x] **T038 — Implementar `ControlNotificaciones` (RF8, C-3)** · 30 min
  - Generar, listar por destinatario y marcar alertas como leídas.
  - **Hecho cuando:** tests de generación por tipo, filtrado por usuario/rol y
    marcado como leída pasan.

## Fase 4 — GUI de consola

- [x] **T039 — Implementar abstracción de consola** · 20 min
  - Interfaz de lectura/escritura inyectable y consola real basada en
    `input`/`print`.
  - **Hecho cuando:** tests verifican lectura programada y captura de salida.

- [x] **T040 — Implementar menú de login y registro (RF1, RF2, C-1)** · 30 min
  - Flujo de registro y login, mensajes de error y creación de sesión.
  - **Hecho cuando:** tests E2E de consola cubren registro válido, login válido
    y credenciales inválidas.

- [x] **T041 — Implementar menús por rol (RF2)** · 30 min
  - Menú de cliente y menú de representante con opciones permitidas.
  - **Hecho cuando:** tests verifican que cada rol ve solo sus opciones y que
    logout vuelve al menú inicial.

- [x] **T042 — Implementar flujo Crear Ticket (RF3, C-2)** · 30 min
  - Selección de tipo/producto, captura de datos y confirmación.
  - **Hecho cuando:** test E2E con consola simulada crea el ticket y muestra su
    identificador.

- [x] **T043 — Implementar flujo Asignar Ticket (RF4)** · 25 min
  - Listado de tickets nuevos y selección de representante.
  - **Hecho cuando:** test E2E verifica la asignación y el mensaje de
    confirmación.

- [x] **T044 — Implementar flujo de Mensajes (RF5)** · 25 min
  - Ver, enviar y listar mensajes de un ticket.
  - **Hecho cuando:** test E2E verifica envío, visualización y error de acceso
    ajeno.

- [x] **T045 — Implementar flujo de Hitos (RF6)** · 25 min
  - Crear, actualizar y completar hitos desde consola.
  - **Hecho cuando:** test E2E verifica alta y completado de hitos y la
    resolución del ticket.

- [x] **T046 — Implementar flujo Revisar Alertas (RF8, C-3)** · 25 min
  - Listar alertas pendientes, mostrar detalle y marcar como leída.
  - **Hecho cuando:** test E2E verifica listado, detalle, marcado y caso "sin
    alertas".

- [x] **T047 — Implementar flujo Cierre y Reapertura (RF9, RF10)** · 30 min
  - Cierre con comentario y reapertura con motivo.
  - **Hecho cuando:** test E2E verifica cierre, reapertura y bloqueo de
    operaciones en estado `CERRADO`.

- [x] **T048 — Implementar manejo de errores y entradas inválidas en GUI** · 25 min
  - Capturar errores de dominio, validar opciones numéricas y evitar
    tracebacks.
  - **Hecho cuando:** tests de entrada no numérica, opción inexistente y error
    de dominio muestran mensajes claros sin traceback.

- [x] **T049 — Implementar `main.py` y wiring de la aplicación** · 25 min
  - Resolver ruta, abrir conexión, crear esquema, cargar datos iniciales,
    instanciar repositorios/controladores/GUI e iniciar.
  - **Hecho cuando:** un test de humo construye la aplicación con una DB
    temporal y verifica el arranque.

## Fase 5 — Integración y cierre

- [x] **T050 — Escribir test E2E completo RF1–RF10** · 30 min
  - Flujo: registro de cliente y representante, login, crear ticket, asignar,
    mensajes, hitos, alertas, cierre y reapertura.
  - **Hecho cuando:** un único test E2E recorre el ciclo completo y verifica
    estados, historial y alertas.

- [x] **T051 — Verificar reglas de dependencia entre capas** · 25 min
  - Test o script que detecte imports prohibidos (`gui`→`db`, `models`→`db`,
    etc.).
  - **Hecho cuando:** la verificación pasa y falla si se introduce un import
    prohibido de prueba.

- [x] **T052 — Verificar nomenclatura y textos en español** · 20 min
  - Revisar PascalCase en clases, camelCase en métodos y mensajes de UI en
    español.
  - **Hecho cuando:** checklist de §18 de `plan.md` completo sin pendientes.

- [x] **T053 — Ejecutar suite completa y medir cobertura** · 30 min
  - Correr pytest completo y generar reporte de cobertura.
  - **Hecho cuando:** 0 fallos, 0 errores y cobertura de los módulos de negocio
    acorde al objetivo acordado.

- [x] **T054 — Revisar criterios de aceptación de `spec.md`** · 30 min
  - Recorrer RF1–RF10 y marcar cada criterio con el test que lo cubre.
  - **Hecho cuando:** todos los criterios de aceptación tienen un test asociado
    y pasan.

- [x] **T055 — Actualizar `MEMORY.md` y estado de implementación** · 20 min
  - Marcar tareas completadas y dejar registrado el estado real del proyecto.
  - **Hecho cuando:** `MEMORY.md` refleja spec, plan, tasks e implementación con
    sus checkboxes correctos.

## Resumen de estimaciones

| Fase | Tareas | Estimación aproximada |
|---|---|---|
| 0 — Preparación | T001–T004 | 1 h 35 min |
| 1 — Modelos | T005–T012 | 3 h 40 min |
| 2 — Persistencia | T013–T025 | 5 h 30 min |
| 3 — Controladores | T026–T038 | 6 h 30 min |
| 4 — GUI | T039–T049 | 4 h 55 min |
| 5 — Integración y cierre | T050–T055 | 2 h 55 min |
| **Total** | **55 tareas** | **≈ 25 h** |

## Regla de avance

1. Tomar la primera tarea pendiente que no dependa de otra incompleta.
2. Escribir el test y confirmar que falla.
3. Implementar hasta que pase.
4. Ejecutar la suite completa.
5. Marcar la tarea como completada solo si la suite está en verde.
6. Detenerse y reportar si una tarea excede los 30 minutos.
