# AGENTS.md - Reglas del Proyecto Ticketing

## Stack
- Python 3.10+ / SQLite (sqlite3)
- Tests con pytest

## Arquitectura
- Separación estricta en capas:
  - `src/models/`: Entidades puras (Usuario, Cliente, Ticket, Hito, Mensaje, Producto, TipoProducto).
  - `src/db/`: Persistencia (SQLite).
  - `src/controller/`: Lógica (ControlTicket, ControlHito, ControlNotificaciones).
  - `src/gui/`: Interfaz por consola (GUI).
- Nada de frameworks web. Solo Python puro.

## Código
- Clases en PascalCase, métodos en camelCase (como en el UML).
- Comentarios y mensajes de UI en español.

## Reglas de Oro
- TDD obligatorio: primero el test (rojo), luego el código (verde).
- NO avanzar si hay tests en rojo.
- NO escribir código sin antes mostrar un plan.