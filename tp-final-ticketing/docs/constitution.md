# Constitución del Proyecto — Sistema de Ticketing

| Campo | Valor |
|---|---|
| Versión | 1.0 |
| Fecha | 2026-11-12 |
| Estado | Vigente |
| Alcance | Todo el repositorio `tp-final-ticketing` |

> Estos seis principios son **innegociables**. Ninguna tarea, cambio o pull
> request puede violarlos. Si una necesidad real exige modificarlos, primero se
> debe acordar y documentar una enmienda explícita a esta constitución.

## 1. Stack y alcance tecnológico

- Python 3.10 o superior.
- Persistencia exclusiva con SQLite mediante `sqlite3` de la biblioteca estándar.
- Interfaz por consola (`input`/`print`), sin frameworks web.
- Pruebas automatizadas con `pytest`.
- Sin dependencias externas de runtime; solo biblioteca estándar.
- Rutas con `pathlib.Path` y codificación UTF-8 explícita.
- Fuera de alcance: API REST, interfaz web, ORMs y servicios externos.

**Verificación:** el proyecto se ejecuta y testea sin instalar dependencias de
runtime; no existen imports de frameworks web ni de ORMs.

## 2. TDD obligatorio

- Todo código de producción nace de un test que primero falla (rojo).
- Luego se implementa lo mínimo para que pase (verde).
- Después se refactoriza sin romper la suite.
- No se avanza a la siguiente tarea si hay tests en rojo.
- Cada requisito funcional (RF) debe tener al menos un test de aceptación.

**Verificación:** la suite completa de `pytest` pasa en verde y existe
trazabilidad entre cada RF y sus tests.

## 3. Separación estricta en capas

El flujo de dependencias permitido es:

```text
gui ──> controller ──> db ──> models
```

Reglas obligatorias:

- `models` no importa `db`, `controller`, `gui` ni `sqlite3`.
- `db` puede importar `models`; no importa `controller` ni `gui`.
- `controller` puede importar `models` y `db`; no importa `gui`.
- `gui` puede importar `controller` y `models`; no importa `db` ni `sqlite3`.
- Todo acceso a SQLite vive exclusivamente en `src/db/`.

**Verificación:** test automatizado de imports que detecte cualquier violación
entre capas.

## 4. Modelos puros y persistencia encapsulada

- Los modelos son entidades puras con invariantes y reglas de negocio simples:
  no conocen SQLite, consola ni controladores.
- Toda la persistencia está encapsulada en `src/db/`; no se exponen cursores ni
  SQL fuera de esa capa.
- Los repositorios reciben una conexión por inyección de dependencias.
- Las operaciones que afectan varias tablas se ejecutan en una transacción.
- La máquina de estados del ticket tiene una única fuente de verdad en
  `models/estados.py`; toda transición no declarada se rechaza.
- El historial es de solo inserción y lectura: no se actualiza ni se elimina.

**Verificación:** tests de repositorios contra SQLite temporal, tests de
transacciones y tests de transiciones permitidas/prohibidas.

## 5. GUI delgada y controladores como casos de uso

- La GUI solo presenta, captura y delega; no contiene reglas de negocio ni SQL.
- Los controladores orquestan modelos, repositorios y notificaciones, validan
  permisos según rol y traducen errores técnicos a errores de dominio.
- Las dependencias (conexión, consola, reloj) se inyectan; no hay estado global
  mutable.
- La GUI captura `ErrorDominio` y muestra mensajes claros en español, sin
  tracebacks ni detalles técnicos.

**Verificación:** tests de GUI con consola simulada y tests de controladores con
dependencias inyectadas.

## 6. Convenciones, seguridad y trazabilidad

- Clases en `PascalCase` y métodos en `camelCase`, respetando el UML.
- Comentarios y mensajes de interfaz en español.
- Errores de dominio explícitos en `src/excepciones.py`.
- Contraseñas almacenadas con PBKDF2-HMAC-SHA256 y salt, verificadas en tiempo
  constante; nunca en texto plano, logs o mensajes de error.
- Toda operación relevante registra historial y, cuando corresponde, genera
  alertas.
- El cierre y la reapertura de tickets respetan la máquina de estados y quedan
  auditados.

**Verificación:** revisión de nomenclatura e idioma, tests de seguridad de
contraseñas, tests de historial y tests de aceptación de RF1–RF10.

## Cumplimiento

- Cada tarea y pull request debe verificar el cumplimiento de estos seis
  principios antes de considerarse terminado.
- Ante una violación, se detiene el avance y se corrige antes de continuar.
- Esta constitución complementa `AGENTS.md`, `spec.md`, `plan.md` y `tasks.md`.
  Los detalles operativos viven en esos documentos; los principios aquí
  establecidos prevalecen ante decisiones tácticas que los contradigan.
