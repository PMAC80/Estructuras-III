ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('CLIENTE', 'REPRESENTANTE')),
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS cliente (
    id_usuario INTEGER PRIMARY KEY
        REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    empresa TEXT,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS representante (
    id_usuario INTEGER PRIMARY KEY
        REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    legajo TEXT UNIQUE,
    especialidad TEXT
);

CREATE TABLE IF NOT EXISTS tipo_producto (
    id_tipo_producto INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    version TEXT NOT NULL,
    id_tipo_producto INTEGER NOT NULL
        REFERENCES tipo_producto(id_tipo_producto) ON DELETE RESTRICT,
    UNIQUE (nombre, version, id_tipo_producto)
);

CREATE TABLE IF NOT EXISTS ticket (
    id_ticket INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (
        estado IN (
            'NUEVO',
            'ASIGNADO',
            'EN_PROGRESO',
            'RESUELTO',
            'CERRADO',
            'REABIERTO'
        )
    ),
    prioridad TEXT NOT NULL CHECK (prioridad IN ('BAJA', 'MEDIA', 'ALTA')),
    fecha_creacion TEXT NOT NULL,
    fecha_cierre TEXT,
    id_cliente INTEGER NOT NULL
        REFERENCES cliente(id_usuario) ON DELETE RESTRICT,
    id_representante INTEGER
        REFERENCES representante(id_usuario) ON DELETE RESTRICT,
    id_producto INTEGER NOT NULL
        REFERENCES producto(id_producto) ON DELETE RESTRICT,
    id_tipo_producto INTEGER NOT NULL
        REFERENCES tipo_producto(id_tipo_producto) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS hito (
    id_hito INTEGER PRIMARY KEY,
    id_ticket INTEGER NOT NULL
        REFERENCES ticket(id_ticket) ON DELETE RESTRICT,
    descripcion TEXT NOT NULL,
    fecha_compromiso TEXT NOT NULL,
    fecha_cumplimiento TEXT,
    estado TEXT NOT NULL CHECK (
        estado IN ('PENDIENTE', 'EN_PROGRESO', 'CUMPLIDO', 'VENCIDO')
    ),
    orden INTEGER NOT NULL CHECK (orden > 0),
    UNIQUE (id_ticket, orden)
);

CREATE TABLE IF NOT EXISTS mensaje (
    id_mensaje INTEGER PRIMARY KEY,
    id_ticket INTEGER NOT NULL
        REFERENCES ticket(id_ticket) ON DELETE RESTRICT,
    id_autor INTEGER NOT NULL
        REFERENCES usuario(id_usuario) ON DELETE RESTRICT,
    contenido TEXT NOT NULL,
    fecha_envio TEXT NOT NULL,
    leido INTEGER NOT NULL DEFAULT 0 CHECK (leido IN (0, 1))
);

CREATE TABLE IF NOT EXISTS historial (
    id_evento INTEGER PRIMARY KEY,
    id_ticket INTEGER NOT NULL
        REFERENCES ticket(id_ticket) ON DELETE RESTRICT,
    id_actor INTEGER
        REFERENCES usuario(id_usuario) ON DELETE SET NULL,
    tipo_evento TEXT NOT NULL,
    estado_anterior TEXT,
    estado_nuevo TEXT,
    detalle TEXT,
    fecha TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerta (
    id_alerta INTEGER PRIMARY KEY,
    id_usuario INTEGER NOT NULL
        REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    id_ticket INTEGER
        REFERENCES ticket(id_ticket) ON DELETE CASCADE,
    tipo TEXT NOT NULL,
    prioridad TEXT NOT NULL CHECK (prioridad IN ('BAJA', 'MEDIA', 'ALTA')),
    mensaje TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('PENDIENTE', 'LEIDA')),
    fecha_creacion TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ticket_estado ON ticket(estado);
CREATE INDEX IF NOT EXISTS idx_ticket_cliente ON ticket(id_cliente);
CREATE INDEX IF NOT EXISTS idx_ticket_representante ON ticket(id_representante);
CREATE INDEX IF NOT EXISTS idx_alerta_usuario_estado ON alerta(id_usuario, estado);
CREATE INDEX IF NOT EXISTS idx_hito_ticket ON hito(id_ticket);
CREATE INDEX IF NOT EXISTS idx_mensaje_ticket ON mensaje(id_ticket);
CREATE INDEX IF NOT EXISTS idx_historial_ticket ON historial(id_ticket);
CREATE INDEX IF NOT EXISTS idx_producto_tipo ON producto(id_tipo_producto);
"""


def crearEsquema(conexion) -> None:
    conexion.executescript(ESQUEMA_SQL)
