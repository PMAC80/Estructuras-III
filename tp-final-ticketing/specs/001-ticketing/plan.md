# Plan Técnico — Sistema de Ticketing

## 1. Contexto técnico

| Aspecto | Decisión |
|---|---|
| Lenguaje | Python 3.10+ |
| Persistencia | SQLite mediante `sqlite3` (stdlib) |
| Interfaz | Consola (`input`/`print`), sin frameworks web |
| Testing | pytest (dependencia de desarrollo) |
| Dependencias de runtime | Solo biblioteca estándar |
| Codificación | UTF-8 |
| Rutas | `pathlib.Path` |
| Base de datos | Archivo local `ticketing.db` (configurable) |

Este plan traduce `specs/001-ticketing/spec.md` a una arquitectura técnica. No
incluye código de implementación; define componentes, decisiones y secuencia.

## 2. Principios de arquitectura

1. **Separación estricta en capas:** `models` → `db` → `controller` → `gui`.
2. **Modelos puros:** no conocen SQLite, consola ni controladores.
3. **GUI delgada:** solo presenta, captura y delega; no contiene reglas de
   negocio ni SQL.
4. **Controladores como casos de uso:** orquestan modelos, repositorios y
   notificaciones.
5. **Persistencia encapsulada:** todo acceso a SQLite vive en `src/db/`.
6. **TDD:** primero el test en rojo, luego la implementación mínima en verde.
7. **Reglas de estado centralizadas:** una única fuente de verdad para las
   transiciones del ticket.
8. **Errores de dominio explícitos:** mensajes en español, sin filtrar detalles
   técnicos al usuario.
9. **Nomenclatura:** clases en PascalCase, métodos en camelCase.
10. **Sin estado global mutable:** conexiones y sesiones se inyectan.

## 3. Estructura de directorios propuesta

```text
tp-final-ticketing/
├── src/
│   ├── __init__.py
│   ├── excepciones.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── estados.py
│   │   ├── seguridad.py
│   │   ├── usuario.py
│   │   ├── cliente.py
│   │   ├── representante.py
│   │   ├── tipo_producto.py
│   │   ├── producto.py
│   │   ├── ticket.py
│   │   ├── hito.py
│   │   └── mensaje.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── conexion.py
│   │   ├── esquema.py
│   │   ├── mapeo.py
│   │   ├── datos_iniciales.py
│   │   └── repositorios/
│   │       ├── __init__.py
│   │       ├── repositorio_usuario.py
│   │       ├── repositorio_cliente.py
│   │       ├── repositorio_representante.py
│   │       ├── repositorio_tipo_producto.py
│   │       ├── repositorio_producto.py
│   │       ├── repositorio_ticket.py
│   │       ├── repositorio_hito.py
│   │       ├── repositorio_mensaje.py
│   │       ├── repositorio_historial.py
│   │       └── repositorio_alerta.py
│   ├── controller/
│   │   ├── __init__.py
│   │   ├── sesion.py
│   │   ├── control_usuario.py
│   │   ├── control_ticket.py
│   │   ├── control_hito.py
│   │   └── control_notificaciones.py
│   └── gui/
│       ├── __init__.py
│       ├── consola.py
│       ├── menus.py
│       └── gui.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── specs/001-ticketing/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── main.py
├── pyproject.toml
├── AGENTS.md
└── MEMORY.md
```

Notas:

- `ticketing.db` se crea en tiempo de ejecución y no se versiona.
- `pyproject.toml` solo configura pytest y metadatos del proyecto.
- `src/excepciones.py` centraliza errores de dominio.

## 4. Diseño por capas

### 4.1 Capa `models`

Entidades puras con validaciones de invariantes y métodos de negocio simples.

| Componente | Responsabilidad |
|---|---|
| `estados.py` | Constantes de estado/prioridad/rol y tabla de transiciones permitidas. |
| `seguridad.py` | Hash y verificación de contraseñas con PBKDF2-HMAC-SHA256 + salt. |
| `Usuario` | Identidad, rol y estado activo. |
| `Cliente` | Extiende `Usuario`; datos de empresa y teléfono. |
| `Representante` | Extiende `Usuario`; legajo y especialidad. |
| `TipoProducto` | Categoría de producto. |
| `Producto` | Producto asociado a un tipo. |
| `Ticket` | Datos del ticket y validación de transiciones de estado. |
| `Hito` | Etapa del ticket, vencimiento y cumplimiento. |
| `Mensaje` | Comunicación asociada a un ticket. |

Lineamientos:

- Sin imports de `sqlite3`, `db`, `controller` ni `gui`.
- Validaciones en constructores o métodos `validar()`.
- Fechas inyectables para facilitar pruebas deterministas.

### 4.2 Capa `db`

Encapsula conexión, esquema, mapeo y repositorios.

| Componente | Responsabilidad |
|---|---|
| `conexion.py` | Abrir/cerrar conexión, `row_factory`, `PRAGMA foreign_keys = ON`, contexto transaccional. |
| `esquema.py` | Crear tablas e índices de forma idempotente. |
| `mapeo.py` | Conversión entre filas SQLite (`snake_case`) y entidades (`camelCase`). |
| `datos_iniciales.py` | Carga idempotente de tipos de producto y productos base. |
| `repositorio_*` | Operaciones CRUD y consultas por entidad. |

Lineamientos:

- Cada repositorio recibe una conexión; no abre conexiones propias.
- Las operaciones que modifican estado e historial se ejecutan en una misma
  transacción.
- No se exponen cursores ni SQL fuera de la capa `db`.
- `historial` es de solo inserción y lectura.
- No se implementan métodos de actualización/borrado sobre `historial`.

### 4.3 Capa `controller`

Orquesta casos de uso y reglas de negocio.

| Componente | Responsabilidad |
|---|---|
| `ControlUsuario` | Registro, login, logout y consulta de sesión. Extensión auxiliar justificada (ver §12). |
| `ControlTicket` | Crear, asignar, cambiar estado, mensajes, cerrar, reabrir e historial. |
| `ControlHito` | Crear, actualizar, completar hitos y detectar vencidos. |
| `ControlNotificaciones` | Generar, listar y marcar alertas. |
| `sesion.py` | Estructura inmutable de sesión (`idUsuario`, `rol`, `nombre`). |

Lineamientos:

- Reciben repositorios por inyección de dependencias.
- Validan permisos según rol y pertenencia al ticket.
- Traducen errores de persistencia a errores de dominio.
- Registran historial y disparan alertas en la misma operación de negocio.
- No leen `input` ni escriben en consola.

### 4.4 Capa `gui`

Interfaz por consola, testeable mediante inyección de entrada/salida.

| Componente | Responsabilidad |
|---|---|
| `consola.py` | Abstracción de entrada/salida (`leer`, `escribir`) para pruebas. |
| `menus.py` | Definición de menús por rol y textos en español. |
| `gui.py` | Flujos de login, registro, tickets, hitos, mensajes, alertas y cierre/reapertura. |

Lineamientos:

- `GUI` recibe controladores y una implementación de consola.
- No importa `sqlite3` ni `src.db`.
- Captura errores de dominio y muestra mensajes claros.
- Mantiene la sesión activa en memoria y la descarta al cerrar sesión.

## 5. Reglas de dependencia

```text
gui ──> controller ──> db ──> models
 │            │          │
 └────────────┴──────────┴──> models (solo entidades y errores)
```

Reglas verificables:

- `gui` no importa `db` ni `sqlite3`.
- `models` no importa `db`, `controller` ni `gui`.
- `db` puede importar `models`; no importa `controller` ni `gui`.
- `controller` puede importar `models` y `db`; no importa `gui`.
- Un test estático (o revisión automatizada de imports) valida estas reglas.

## 6. Persistencia

### 6.1 Conexión

- Función `abrirConexion(ruta)` que:
  - crea directorios si faltan;
  - configura `row_factory = sqlite3.Row`;
  - ejecuta `PRAGMA foreign_keys = ON`;
  - usa `isolation_level` explícito para transacciones controladas.
- Cierre garantizado con context manager.
- Una conexión por operación de negocio o por sesión de aplicación de consola.

### 6.2 Esquema

- Creación idempotente con `CREATE TABLE IF NOT EXISTS`.
- Tablas según §11 de `spec.md`: `usuario`, `cliente`, `representante`,
  `tipo_producto`, `producto`, `ticket`, `hito`, `mensaje`, `historial`,
  `alerta`.
- Restricciones `CHECK` para estados, prioridades y roles.
- Índices en claves foráneas y en `ticket.estado`, `alerta.estado`,
  `usuario.email`.

### 6.3 Repositorios

| Repositorio | Operaciones principales |
|---|---|
| `RepositorioUsuario` | insertar, buscar por email, buscar por id, activar/desactivar |
| `RepositorioCliente` | insertar, buscar por id de usuario |
| `RepositorioRepresentante` | insertar, buscar por id, listar activos |
| `RepositorioTipoProducto` | insertar, listar, buscar por id |
| `RepositorioProducto` | insertar, listar por tipo, buscar por id |
| `RepositorioTicket` | insertar, buscar, listar por cliente/representante, actualizar estado/asignación, listar sin asignar |
| `RepositorioHito` | insertar, buscar, listar por ticket, actualizar, listar vencidos |
| `RepositorioMensaje` | insertar, listar por ticket, marcar leído |
| `RepositorioHistorial` | insertar, listar por ticket (orden ascendente) |
| `RepositorioAlerta` | insertar, listar por usuario/rol, marcar leída, listar pendientes |

### 6.4 Transacciones

- Alta de ticket = insertar ticket + insertar historial en una transacción.
- Asignación = actualizar ticket + historial + alerta.
- Cierre/reapertura = actualizar ticket + historial + alerta.
- Mensaje = insertar mensaje + historial + alerta.
- Ante cualquier error, rollback completo y error de dominio.

## 7. Seguridad

- Hash: PBKDF2-HMAC-SHA256 con `hashlib.pbkdf2_hmac`.
- Salt: `secrets.token_bytes(16)` por usuario.
- Iteraciones: mínimo 200.000 (configurable por constante).
- Formato almacenado: `pbkdf2_sha256$<iteraciones>$<salt_hex>$<hash_hex>`.
- Verificación con `hmac.compare_digest` (tiempo constante).
- La contraseña nunca se registra en logs, historial ni mensajes de error.
- El login devuelve un mensaje genérico ante credenciales inválidas.
- Los usuarios inactivos no pueden autenticarse.

## 8. Sesión y roles

- `Sesion` es una estructura inmutable (dataclass) con `idUsuario`, `nombre`,
  `rol`.
- Vive en memoria durante la ejecución de la consola.
- `ControlUsuario` crea y destruye la sesión.
- Cada controlador valida:
  - que exista sesión;
  - que el rol tenga permiso;
  - que el usuario acceda solo a tickets propios o asignados.
- Operaciones por rol:
  - Cliente: crear ticket, ver sus tickets, mensajes, reabrir.
  - Representante: asignar, hitos, mensajes, cerrar, reabrir según permisos.

## 9. Máquina de estados

- Constantes en `models/estados.py`.
- Tabla `TRANSICIONES` con pares `(estadoOrigen, evento) -> estadoDestino`.
- `Ticket.cambiarEstado(evento)` valida contra la tabla y lanza
  `ErrorEstado` si la transición no existe.
- `ControlTicket` es el único que persiste cambios de estado.
- `ControlHito` solicita a `ControlTicket` la transición a `RESUELTO` al
  completar el último hito.
- Cualquier transición no listada en §12 de `spec.md` es rechazada y no se
  persiste.

## 10. Historial y alertas (transversal)

### 10.1 Historial

- Se escribe únicamente desde los controladores, a través de
  `RepositorioHistorial`.
- Campos: ticket, actor, tipo de evento, estado anterior, estado nuevo,
  detalle, fecha.
- Sin operaciones de actualización ni borrado.
- Orden de lectura: fecha ascendente.

### 10.2 Alertas

- Generadas por `ControlNotificaciones` a pedido de los controladores.
- Tipos iniciales:
  - `TICKET_SIN_ASIGNAR` (> 24 h sin asignar).
  - `HITO_VENCIDO`.
  - `MENSAJE_NUEVO`.
  - `CAMBIO_ESTADO`.
  - `REAPERTURA`.
- Estados: `PENDIENTE`, `LEIDA`.
- Consulta filtrada por usuario destinatario o rol.
- Tiempo inyectable (reloj) para pruebas deterministas.

## 11. Manejo de errores

Jerarquía propuesta en `src/excepciones.py`:

| Excepción | Uso |
|---|---|
| `ErrorDominio` | Base de errores de negocio. |
| `ErrorValidacion` | Datos de entrada inválidos. |
| `ErrorAutenticacion` | Credenciales inválidas o usuario inactivo. |
| `ErrorPermiso` | Operación no autorizada para el rol/usuario. |
| `ErrorEstado` | Transición de estado inválida. |
| `ErrorNoEncontrado` | Entidad inexistente. |
| `ErrorConflicto` | Duplicados (email, legajo). |

Lineamientos:

- Los repositorios lanzan errores técnicos acotados o `ErrorConflicto`.
- Los controladores traducen a errores de dominio con mensajes en español.
- La GUI captura `ErrorDominio` y muestra `str(error)`.
- Errores inesperados se muestran como mensaje genérico; nunca con traceback.

## 12. Extensión justificada del UML

El UML provisto define `ControlTicket`, `ControlHito` y `ControlNotificaciones`,
pero no un controlador de acceso. Para no violar la regla "la GUI no accede a
`db`", se agrega **`ControlUsuario`** como controlador auxiliar de registro,
login y logout.

- No reemplaza ni modifica los tres controladores del UML.
- Mantiene la separación de capas y la testabilidad.
- Si se exige adherencia estricta al UML, la alternativa es mover esa lógica a
  un servicio de aplicación dentro de `src/controller/` con otro nombre; el
  diseño de repositorios no cambia.

## 13. Estrategia de testing (TDD)

### 13.1 Tipos de prueba

| Nivel | Ubicación | Alcance |
|---|---|---|
| Unitario | `tests/unit/` | Modelos, seguridad, estados, validaciones. |
| Integración | `tests/integration/` | Repositorios contra SQLite temporal. |
| Controladores | `tests/integration/` | Casos de uso con repositorios reales en DB temporal. |
| E2E de consola | `tests/e2e/` | Flujos completos con entrada/salida simulada. |

### 13.2 Infraestructura de pruebas

- `tests/conftest.py` con fixtures:
  - `db_temporal`: archivo SQLite en `tmp_path`, esquema creado, borrado al
    finalizar.
  - `db_en_memoria`: variante `:memory:` para pruebas rápidas.
  - `repositorios`: instancias conectadas a la DB de prueba.
  - `controladores`: instancias con repositorios inyectados.
  - `consola_fake`: entrada programada y salida capturada.
  - `reloj_fijo`: fecha/hora determinista para hitos y alertas.
- Sin estado compartido entre tests.
- Sin dependencia de la base `ticketing.db` real.

### 13.3 Reglas TDD

1. Escribir el test que falla.
2. Implementar lo mínimo para que pase.
3. Refactorizar sin romper tests.
4. No avanzar con tests en rojo.
5. Cada RF debe tener al menos un test de aceptación.

## 14. Datos iniciales

- `datos_iniciales.py` carga, de forma idempotente:
  - tipos de producto base;
  - productos de ejemplo asociados.
- Se ejecuta al inicializar la aplicación.
- No duplica registros existentes (clave natural por nombre/versión).
- Los datos maestros no se gestionan por GUI en esta versión.

## 15. Configuración

- `TICKETING_DB_PATH` (variable de entorno) define la ruta de la base.
- Valor por defecto: `ticketing.db` en la raíz del proyecto.
- `main.py`:
  1. resuelve la ruta;
  2. abre conexión;
  3. crea esquema;
  4. carga datos iniciales;
  5. instancia repositorios, controladores y GUI;
  6. inicia la consola.
- Sin credenciales ni secretos en el repositorio.

## 16. Secuencia de implementación

1. **Preparación:** estructura, pytest, configuración, excepciones.
2. **Modelos:** entidades, seguridad, estados; tests unitarios.
3. **Persistencia:** conexión, esquema, repositorios, transacciones, seed.
4. **Controladores:** auth, tickets, hitos, notificaciones; tests de casos de uso.
5. **GUI:** menús y flujos; tests con consola simulada.
6. **Integración:** flujo E2E RF1–RF10, revisión de capas y nomenclatura.
7. **Cierre:** suite completa en verde, cobertura y actualización de `MEMORY.md`.

El detalle accionable está en `specs/001-ticketing/tasks.md`.

## 17. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Violación de capas | Alto | Test de imports y revisión por PR/tarea. |
| Inconsistencia de estados | Alto | Tabla única de transiciones + transacciones. |
| Contraseñas inseguras | Alto | PBKDF2 + salt + comparación en tiempo constante. |
| Tests dependientes del tiempo | Medio | Reloj inyectable y fechas fijas en fixtures. |
| SQLite bloqueada por concurrencia | Bajo | Uso mono-usuario, transacciones cortas. |
| Duplicación de datos iniciales | Medio | Seed idempotente por clave natural. |
| Crecimiento del alcance | Medio | Trazabilidad contra `spec.md`; sin features extra. |
| Errores técnicos visibles al usuario | Medio | Traducción a errores de dominio en controladores. |
| Rutas/encoding en Windows | Bajo | `pathlib`, UTF-8 explícito. |

## 18. Definition of Done

- [x] Todos los RF de `spec.md` tienen tests de aceptación en verde.
- [x] Los casos de uso C-1, C-2 y C-3 están cubiertos por tests E2E.
- [x] La suite completa de pytest pasa sin fallos ni errores.
- [x] No existen imports que violen las reglas de capas.
- [x] No se usa ningún framework web ni dependencia externa de runtime.
- [x] La nomenclatura respeta PascalCase/camelCase y los textos están en español.
- [x] Las contraseñas se almacenan hasheadas y nunca se registran.
- [x] El historial es inmutable y toda operación relevante queda registrada.
- [x] La máquina de estados se respeta en todos los flujos.
- [x] `MEMORY.md` refleja el estado real del proyecto.
