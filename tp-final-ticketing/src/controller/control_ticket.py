from datetime import datetime, timedelta

from src.db.conexion import transaccion
from src.excepciones import (
    ErrorEstado,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    ESTADO_CERRADO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_NUEVO,
    ESTADO_REABIERTO,
    ESTADO_RESUELTO,
    EVENTO_ASIGNAR,
    EVENTO_CERRAR,
    EVENTO_REABRIR,
    PRIORIDAD_ALTA,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)
from src.models.mensaje import Mensaje
from src.models.ticket import Ticket
from src.models.validaciones import validarTextoObligatorio


class ControlTicket:
    def __init__(
        self,
        conexion,
        repositorioTickets,
        repositorioHistorial,
        repositorioMensajes,
        repositorioHitos,
        repositorioProductos,
        repositorioTiposProducto,
        repositorioClientes,
        repositorioRepresentantes,
        controlUsuario,
        controlNotificaciones,
        reloj=None,
    ):
        self.conexion = conexion
        self.repositorioTickets = repositorioTickets
        self.repositorioHistorial = repositorioHistorial
        self.repositorioMensajes = repositorioMensajes
        self.repositorioHitos = repositorioHitos
        self.repositorioProductos = repositorioProductos
        self.repositorioTiposProducto = repositorioTiposProducto
        self.repositorioClientes = repositorioClientes
        self.repositorioRepresentantes = repositorioRepresentantes
        self.controlUsuario = controlUsuario
        self.controlNotificaciones = controlNotificaciones
        self.reloj = reloj or datetime.now

    def _ahora(self):
        return self.reloj()

    def crearTicket(
        self,
        titulo,
        descripcion,
        prioridad,
        idProducto,
        idTipoProducto,
        fecha=None,
    ):
        sesion = self.controlUsuario.requerirRol(ROL_CLIENTE)

        producto = self.repositorioProductos.buscarPorId(idProducto)
        if producto is None:
            raise ErrorNoEncontrado("El producto indicado no existe.")
        if producto.idTipoProducto != idTipoProducto:
            raise ErrorValidacion(
                "El producto no pertenece al tipo de producto indicado."
            )
        if self.repositorioClientes.buscarPorId(sesion.idUsuario) is None:
            raise ErrorNoEncontrado("El cliente de la sesión no existe.")

        ticket = Ticket(
            titulo,
            descripcion,
            prioridad,
            sesion.idUsuario,
            idProducto,
            idTipoProducto,
            fechaCreacion=fecha or self._ahora(),
        )

        with transaccion(self.conexion):
            ticket.idTicket = self.repositorioTickets.insertar(ticket)
            self.repositorioHistorial.insertar(
                ticket.idTicket,
                sesion.idUsuario,
                "CREACION",
                None,
                ESTADO_NUEVO,
                "Ticket creado.",
                self._ahora(),
            )

        return ticket

    def asignarTicket(self, idTicket, idRepresentante):
        sesion = self.controlUsuario.requerirRol(ROL_REPRESENTANTE)

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")

        representante = self.repositorioRepresentantes.buscarPorId(
            idRepresentante
        )
        if representante is None:
            raise ErrorNoEncontrado("El representante indicado no existe.")
        if not representante.activo:
            raise ErrorEstado("El representante no está activo.")

        estadoAnterior = ticket.estado
        ticket.cambiarEstado(EVENTO_ASIGNAR)
        ticket.idRepresentante = idRepresentante

        with transaccion(self.conexion):
            self.repositorioTickets.asignar(idTicket, idRepresentante)
            self.repositorioTickets.actualizarEstado(
                idTicket,
                ticket.estado,
                ticket.fechaCierre,
            )
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "ASIGNACION",
                estadoAnterior,
                ticket.estado,
                f"Ticket asignado a {representante.nombre}.",
                self._ahora(),
            )
            self.controlNotificaciones.generarAlerta(
                idRepresentante,
                idTicket,
                "CAMBIO_ESTADO",
                PRIORIDAD_ALTA,
                f"Se le asignó el ticket #{idTicket}.",
            )

        return ticket

    def cambiarEstado(self, idTicket, evento, fecha=None):
        sesion = self.controlUsuario.requerirRol(ROL_REPRESENTANTE)

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")
        if ticket.idRepresentante != sesion.idUsuario:
            raise ErrorPermiso(
                "No tiene permiso para modificar este ticket."
            )

        estadoAnterior = ticket.estado
        ticket.cambiarEstado(evento, fecha)

        with transaccion(self.conexion):
            self.repositorioTickets.actualizarEstado(
                idTicket,
                ticket.estado,
                ticket.fechaCierre,
            )
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "CAMBIO_ESTADO",
                estadoAnterior,
                ticket.estado,
                f"Evento {evento}.",
                fecha or self._ahora(),
            )
            self.controlNotificaciones.notificarCambioEstado(
                ticket,
                estadoAnterior,
                ticket.estado,
            )

        return ticket

    def cerrarTicket(self, idTicket, comentario=None, fecha=None):
        sesion = self.controlUsuario.requerirSesion()

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")
        if sesion.rol != ROL_REPRESENTANTE:
            raise ErrorPermiso(
                "Solo el representante asignado puede cerrar el ticket."
            )
        if ticket.idRepresentante != sesion.idUsuario:
            raise ErrorPermiso(
                "No tiene permiso para cerrar este ticket."
            )
        if ticket.estado != ESTADO_RESUELTO:
            raise ErrorEstado(
                "Solo se pueden cerrar tickets resueltos."
            )

        hitos = self.repositorioHitos.listarPorTicket(idTicket)
        pendientes = [
            hito
            for hito in hitos
            if hito.estado != ESTADO_HITO_CUMPLIDO
        ]
        justificacion = (
            comentario.strip()
            if comentario is not None
            else None
        )
        if justificacion == "":
            justificacion = None
        if (not hitos or pendientes) and justificacion is None:
            raise ErrorEstado(
                "Debe justificar el cierre porque hay hitos pendientes."
            )
        if justificacion is not None:
            justificacion = validarTextoObligatorio(
                justificacion,
                "comentario",
            )

        estadoAnterior = ticket.estado
        momento = fecha or self._ahora()
        ticket.cambiarEstado(EVENTO_CERRAR, momento)

        with transaccion(self.conexion):
            self.repositorioTickets.actualizarEstado(
                idTicket,
                ticket.estado,
                ticket.fechaCierre,
            )
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "CIERRE",
                estadoAnterior,
                ticket.estado,
                justificacion or "Ticket cerrado.",
                momento,
            )
            self.controlNotificaciones.notificarCambioEstado(
                ticket,
                estadoAnterior,
                ticket.estado,
            )

        return ticket

    def reabrirTicket(self, idTicket, motivo, fecha=None):
        motivo = validarTextoObligatorio(motivo, "motivo")
        sesion = self.controlUsuario.requerirSesion()

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")

        esClientePropietario = (
            sesion.rol == ROL_CLIENTE
            and ticket.idCliente == sesion.idUsuario
        )
        esRepresentanteAsignado = (
            sesion.rol == ROL_REPRESENTANTE
            and ticket.idRepresentante == sesion.idUsuario
        )
        if not (esClientePropietario or esRepresentanteAsignado):
            raise ErrorPermiso(
                "No tiene permiso para reabrir este ticket."
            )
        if ticket.estado != ESTADO_CERRADO:
            raise ErrorEstado("El ticket no está cerrado.")
        if ticket.fechaCierre is None:
            raise ErrorEstado(
                "No se puede determinar la fecha de cierre."
            )

        momento = fecha or self._ahora()
        if momento - ticket.fechaCierre > timedelta(days=7):
            raise ErrorEstado(
                "El plazo de reapertura de 7 días ha vencido."
            )

        estadoAnterior = ticket.estado
        ticket.cambiarEstado(EVENTO_REABRIR, momento)
        ticket.idRepresentante = None

        with transaccion(self.conexion):
            self.repositorioTickets.actualizarEstado(
                idTicket,
                ticket.estado,
                None,
            )
            self.repositorioTickets.asignar(idTicket, None)
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "REAPERTURA",
                estadoAnterior,
                ticket.estado,
                motivo,
                momento,
            )
            self.controlNotificaciones.notificarReapertura(
                ticket,
                motivo,
            )

        return ticket

    def agregarMensaje(self, idTicket, contenido, fecha=None):
        sesion = self.controlUsuario.requerirSesion()

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")
        if sesion.idUsuario not in (
            ticket.idCliente,
            ticket.idRepresentante,
        ):
            raise ErrorPermiso(
                "No tiene permiso para participar en este ticket."
            )
        if ticket.estado == ESTADO_CERRADO:
            raise ErrorEstado(
                "No se pueden enviar mensajes a un ticket cerrado."
            )

        mensaje = Mensaje(
            idTicket,
            sesion.idUsuario,
            contenido,
            fechaEnvio=fecha or self._ahora(),
        )

        with transaccion(self.conexion):
            mensaje.idMensaje = self.repositorioMensajes.insertar(mensaje)
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "MENSAJE",
                None,
                None,
                contenido,
                self._ahora(),
            )
            idDestinatario = self._destinatarioMensaje(ticket, sesion)
            if idDestinatario is not None:
                self.controlNotificaciones.notificarMensaje(
                    idTicket,
                    idDestinatario,
                )

        return mensaje

    def listarTickets(self):
        sesion = self.controlUsuario.requerirSesion()
        if sesion.rol == ROL_CLIENTE:
            return self.repositorioTickets.listarPorCliente(
                sesion.idUsuario
            )
        if sesion.rol == ROL_REPRESENTANTE:
            return self.repositorioTickets.listarPorRepresentante(
                sesion.idUsuario
            )
        return []

    def listarTiposProducto(self):
        self.controlUsuario.requerirSesion()
        return self.repositorioTiposProducto.listar()

    def listarProductosDeTipo(self, idTipoProducto):
        self.controlUsuario.requerirSesion()
        return self.repositorioProductos.listarPorTipo(idTipoProducto)

    def listarTicketsNuevos(self):
        self.controlUsuario.requerirRol(ROL_REPRESENTANTE)
        tickets = self.repositorioTickets.listarPorEstado(ESTADO_NUEVO)
        tickets.extend(
            self.repositorioTickets.listarPorEstado(ESTADO_REABIERTO)
        )
        return sorted(tickets, key=lambda ticket: ticket.idTicket)

    def listarRepresentantesActivos(self):
        self.controlUsuario.requerirRol(ROL_REPRESENTANTE)
        return self.repositorioRepresentantes.listarActivos()

    def listarMensajes(self, idTicket):
        self._ticketConAcceso(idTicket)
        return self.repositorioMensajes.listarPorTicket(idTicket)

    def obtenerHistorial(self, idTicket):
        _, _ = self._ticketConAcceso(idTicket)
        return self.repositorioHistorial.listarPorTicket(idTicket)

    def registrarHistorial(
        self,
        idTicket,
        tipoEvento,
        estadoAnterior=None,
        estadoNuevo=None,
        detalle=None,
        idActor=None,
        fecha=None,
    ):
        sesion, _ = self._ticketConAcceso(idTicket)
        return self.repositorioHistorial.insertar(
            idTicket,
            idActor if idActor is not None else sesion.idUsuario,
            tipoEvento,
            estadoAnterior,
            estadoNuevo,
            detalle,
            fecha or self._ahora(),
        )

    def _ticketConAcceso(self, idTicket):
        sesion = self.controlUsuario.requerirSesion()
        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")

        if (
            sesion.rol == ROL_CLIENTE
            and ticket.idCliente != sesion.idUsuario
        ):
            raise ErrorPermiso("No tiene acceso a este ticket.")
        if (
            sesion.rol == ROL_REPRESENTANTE
            and ticket.idRepresentante != sesion.idUsuario
        ):
            raise ErrorPermiso("No tiene acceso a este ticket.")

        return sesion, ticket

    @staticmethod
    def _destinatarioMensaje(ticket, sesion):
        if sesion.idUsuario == ticket.idCliente:
            return ticket.idRepresentante
        return ticket.idCliente
