# MEMORY.md

## Objetivo
Implementar un Sistema de Ticketing en Python puro con SQLite y consola,
respetando la arquitectura por capas y TDD con pytest.

## Estado actual
- [x] Entorno de Python configurado.
- [x] AGENTS.md y MEMORY.md creados.
- [x] Spec redactada.
- [x] Plan redactado.
- [x] Tareas definidas.
- [x] Implementación TDD completa (T001-T055).
  - [x] Fase 0 — Preparación.
  - [x] Fase 1 — Modelos (T005-T012).
  - [x] Fase 2 — Persistencia (T013-T025).
  - [x] Fase 3 — Controladores (T026-T038).
  - [x] Fase 4 — GUI de consola (T039-T049).
  - [x] Fase 5 — Integración y cierre (T050-T055).
- [x] Suite completa: **256 tests en verde**.
- [x] Cobertura total de `src`: **94%**.
- [x] Controladores: **90%–97%** de cobertura.
- [x] Modelos: **92%–100%** de cobertura.
- [x] Sin imports prohibidos entre capas.
- [x] Sin dependencias externas de runtime.
- [x] Matriz de aceptación RF1–RF10 documentada.

## Entregables principales
- `main.py`: resuelve la ruta, crea esquema, carga datos iniciales, arma
  repositorios, controladores y GUI, e inicia la aplicación.
- `src/models/`: entidades puras, estados, transiciones, validaciones y
  hashing PBKDF2.
- `src/db/`: conexión SQLite, esquema, datos iniciales, mapeo y repositorios.
- `src/controller/`: `ControlUsuario`, `ControlTicket`, `ControlHito` y
  `ControlNotificaciones`.
- `src/gui/`: consola inyectable, menús por rol y flujos completos.
- `specs/001-ticketing/aceptacion.md`: matriz de criterios RF1–RF10 y su test.
- `tests/`: pruebas unitarias, integración, E2E, arquitectura y aceptación.

## Comandos
- Suite completa:
  `.\venv\Scripts\python.exe -m pytest -q`
- Suite con cobertura:
  `.\venv\Scripts\python.exe -m pytest -q --cov=src --cov-report=term-missing`
- Aplicación:
  `.\venv\Scripts\python.exe main.py`

## Decisiones relevantes
- `ControlTicket.listarTicketsNuevos()` incluye tickets `NUEVO` y `REABIERTO`
  para permitir la reasignación posterior a una reapertura (RF10).
- La GUI no accede a `db`; sólo usa controladores y modelos.
- El reloj se inyecta en controladores para tests deterministas.
- Las operaciones de cierre y reapertura registran historial y generan alertas.
- `pytest` y `pytest-cov` son dependencias opcionales de desarrollo; no hay
  dependencias externas de runtime.

## Pendientes
- Ninguno. Proyecto completo según `spec.md`, `plan.md` y `tasks.md`.
