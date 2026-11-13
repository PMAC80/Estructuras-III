from datetime import datetime

from src.db.registros import RegistroAlerta, RegistroHistorial
from src.models.cliente import Cliente
from src.models.hito import Hito
from src.models.mensaje import Mensaje
from src.models.producto import Producto
from src.models.representante import Representante
from src.models.ticket import Ticket
from src.models.tipo_producto import TipoProducto
from src.models.usuario import Usuario


def _aISO(valor):
    return valor.isoformat() if valor is not None else None


def _aFecha(valor):
    return datetime.fromisoformat(valor) if valor else None


def filaAUsuario(fila) -> Usuario:
    return Usuario(
        fila["id_usuario"],
        fila["nombre"],
        fila["email"],
        fila["contrasena_hash"],
        fila["rol"],
        bool(fila["activo"]),
    )


def datosUsuario(usuario: Usuario) -> dict:
    return {
        "id_usuario": usuario.idUsuario,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "contrasena_hash": usuario.contrasenaHash,
        "rol": usuario.rol,
        "activo": int(usuario.activo),
    }


def filaACliente(fila) -> Cliente:
    return Cliente(
        fila["id_usuario"],
        fila["nombre"],
        fila["email"],
        fila["contrasena_hash"],
        fila["empresa"],
        fila["telefono"],
        bool(fila["activo"]),
    )


def datosCliente(cliente: Cliente) -> dict:
    return {
        "id_usuario": cliente.idUsuario,
        "nombre": cliente.nombre,
        "email": cliente.email,
        "contrasena_hash": cliente.contrasenaHash,
        "rol": cliente.rol,
        "activo": int(cliente.activo),
        "empresa": cliente.empresa,
        "telefono": cliente.telefono,
    }


def filaARepresentante(fila) -> Representante:
    return Representante(
        fila["id_usuario"],
        fila["nombre"],
        fila["email"],
        fila["contrasena_hash"],
        fila["legajo"],
        fila["especialidad"],
        bool(fila["activo"]),
    )


def datosRepresentante(representante: Representante) -> dict:
    return {
        "id_usuario": representante.idUsuario,
        "nombre": representante.nombre,
        "email": representante.email,
        "contrasena_hash": representante.contrasenaHash,
        "rol": representante.rol,
        "activo": int(representante.activo),
        "legajo": representante.legajo,
        "especialidad": representante.especialidad,
    }


def filaATipoProducto(fila) -> TipoProducto:
    return TipoProducto(
        fila["id_tipo_producto"],
        fila["nombre"],
        fila["descripcion"],
    )


def datosTipoProducto(tipoProducto: TipoProducto) -> dict:
    return {
        "id_tipo_producto": tipoProducto.idTipoProducto,
        "nombre": tipoProducto.nombre,
        "descripcion": tipoProducto.descripcion,
    }


def filaAProducto(fila) -> Producto:
    return Producto(
        fila["id_producto"],
        fila["nombre"],
        fila["version"],
        fila["id_tipo_producto"],
    )


def datosProducto(producto: Producto) -> dict:
    return {
        "id_producto": producto.idProducto,
        "nombre": producto.nombre,
        "version": producto.version,
        "id_tipo_producto": producto.idTipoProducto,
    }


def filaATicket(fila) -> Ticket:
    return Ticket(
        fila["titulo"],
        fila["descripcion"],
        fila["prioridad"],
        fila["id_cliente"],
        fila["id_producto"],
        fila["id_tipo_producto"],
        idTicket=fila["id_ticket"],
        idRepresentante=fila["id_representante"],
        estado=fila["estado"],
        fechaCreacion=_aFecha(fila["fecha_creacion"]),
        fechaCierre=_aFecha(fila["fecha_cierre"]),
    )


def datosTicket(ticket: Ticket) -> dict:
    return {
        "id_ticket": ticket.idTicket,
        "titulo": ticket.titulo,
        "descripcion": ticket.descripcion,
        "estado": ticket.estado,
        "prioridad": ticket.prioridad,
        "fecha_creacion": _aISO(ticket.fechaCreacion),
        "fecha_cierre": _aISO(ticket.fechaCierre),
        "id_cliente": ticket.idCliente,
        "id_representante": ticket.idRepresentante,
        "id_producto": ticket.idProducto,
        "id_tipo_producto": ticket.idTipoProducto,
    }


def filaAHito(fila) -> Hito:
    return Hito(
        fila["id_ticket"],
        fila["descripcion"],
        _aFecha(fila["fecha_compromiso"]),
        idHito=fila["id_hito"],
        orden=fila["orden"],
        estado=fila["estado"],
        fechaCumplimiento=_aFecha(fila["fecha_cumplimiento"]),
    )


def datosHito(hito: Hito) -> dict:
    return {
        "id_hito": hito.idHito,
        "id_ticket": hito.idTicket,
        "descripcion": hito.descripcion,
        "fecha_compromiso": _aISO(hito.fechaCompromiso),
        "fecha_cumplimiento": _aISO(hito.fechaCumplimiento),
        "estado": hito.estado,
        "orden": hito.orden,
    }


def filaAMensaje(fila) -> Mensaje:
    return Mensaje(
        fila["id_ticket"],
        fila["id_autor"],
        fila["contenido"],
        idMensaje=fila["id_mensaje"],
        fechaEnvio=_aFecha(fila["fecha_envio"]),
        leido=bool(fila["leido"]),
    )


def datosMensaje(mensaje: Mensaje) -> dict:
    return {
        "id_mensaje": mensaje.idMensaje,
        "id_ticket": mensaje.idTicket,
        "id_autor": mensaje.idAutor,
        "contenido": mensaje.contenido,
        "fecha_envio": _aISO(mensaje.fechaEnvio),
        "leido": int(mensaje.leido),
    }


def filaAHistorial(fila) -> RegistroHistorial:
    return RegistroHistorial(
        fila["id_evento"],
        fila["id_ticket"],
        fila["id_actor"],
        fila["tipo_evento"],
        fila["estado_anterior"],
        fila["estado_nuevo"],
        fila["detalle"],
        _aFecha(fila["fecha"]),
    )


def datosHistorial(registro: RegistroHistorial) -> dict:
    return {
        "id_evento": registro.idEvento,
        "id_ticket": registro.idTicket,
        "id_actor": registro.idActor,
        "tipo_evento": registro.tipoEvento,
        "estado_anterior": registro.estadoAnterior,
        "estado_nuevo": registro.estadoNuevo,
        "detalle": registro.detalle,
        "fecha": _aISO(registro.fecha),
    }


def filaAAlerta(fila) -> RegistroAlerta:
    return RegistroAlerta(
        fila["id_alerta"],
        fila["id_usuario"],
        fila["id_ticket"],
        fila["tipo"],
        fila["prioridad"],
        fila["mensaje"],
        fila["estado"],
        _aFecha(fila["fecha_creacion"]),
    )


def datosAlerta(registro: RegistroAlerta) -> dict:
    return {
        "id_alerta": registro.idAlerta,
        "id_usuario": registro.idUsuario,
        "id_ticket": registro.idTicket,
        "tipo": registro.tipo,
        "prioridad": registro.prioridad,
        "mensaje": registro.mensaje,
        "estado": registro.estado,
        "fecha_creacion": _aISO(registro.fechaCreacion),
    }
