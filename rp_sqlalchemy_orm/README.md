\# Trabajo Práctico: SQLAlchemy ORM - Relaciones en Bases de Datos Relacionales



\## Descripción

Este proyecto demuestra el uso de \*\*SQLAlchemy 2.0+\*\* (ORM puro) en Python para interactuar con bases de datos SQLite. Se implementan los tres pilares fundamentales del modelo relacional: operaciones CRUD básicas, relaciones Uno a Muchos y relaciones Muchos a Muchos.



\## Archivos del Proyecto



| Archivo | Descripción |

|---------|-------------|

| `crud\_basico.py` | Ejemplo de operaciones CRUD (Crear, Leer, Actualizar, Borrar) con una tabla simple de Usuarios. |

| `relacion\_uno\_a\_muchos.py` | Implementa una relación 1:N entre Usuarios y Posts (un usuario tiene muchos artículos). Incluye borrado en cascada. |

| `relacion\_muchos\_a\_muchos.py` | Implementa una relación N:M entre Posts y Etiquetas usando una tabla de asociación intermedia. |

| `requirements.txt` | Lista de dependencias necesarias para ejecutar el proyecto. |



\## Requisitos Previos

\- Python 3.10 o superior

\- Entorno virtual activado (venv)



\## Instalación y Ejecución



1\. Crear y activar el entorno virtual:

&#x20;  ```bash

&#x20;  python -m venv venv

&#x20;  .\\venv\\Scripts\\activate   # Windows

