from datetime import datetime

from src.db.conexion import transaccion
from src.excepciones import (
    ErrorConflicto,
    ErrorEstado,
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    ESTADO_CERRADO,
    ESTADO_EN_PROGRESO,
    ESTADO_HITO_CUMPLIDO,
    ESTADO_HITO_VENCIDO,
    EVENTO_RESOLVER,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)
from src.models.hito import Hito
from src.models.validaciones import (
    validarEnteroPositivo,
    validarTextoObligatorio,
)


class ControlHito:
    def __init__(
        self,
        conexion,
        repositorioHitos,
        repositorioTickets,
        repositorioHistorial,
        controlUsuario,
        controlNotificaciones,
        controlTicket,
        reloj=None,
    ):
        self.conexion = conexion
        self.repositorioHitos = repositorioHitos
        self.repositorioTickets = repositorioTickets
        self.repositorioHistorial = repositorioHistorial
        self.controlUsuario = controlUsuario
        self.controlNotificaciones = controlNotificaciones
        self.controlTicket = controlTicket
        self.reloj = reloj or datetime.now

    def _ahora(self):
        return self.reloj()

    def crearHito(
        self,
        idTicket,
        descripcion,
        fechaCompromiso,
        orden=1,
        fecha=None,
    ):
        sesion, ticket = self._ticketParaRepresentante(idTicket)

        if not isinstance(fechaCompromiso, datetime):
            raise ErrorValidacion(
                "El campo 'fechaCompromiso' debe ser una fecha válida."
            )
        if fechaCompromiso < ticket.fechaCreacion:
            raise ErrorValidacion(
                "La fecha de compromiso no puede ser anterior a la "
                "creación del ticket."
            )
        if any(
            hito.orden == orden
            for hito in self.repositorioHitos.listarPorTicket(idTicket)
        ):
            raise ErrorConflicto(
                "Ya existe un hito con ese orden en el ticket."
            )

        hito = Hito(
            idTicket,
            descripcion,
            fechaCompromiso,
            orden=orden,
        )

        with transaccion(self.conexion):
            hito.idHito = self.repositorioHitos.insertar(hito)
            self.repositorioHistorial.insertar(
                idTicket,
                sesion.idUsuario,
                "HITO_CREADO",
                None,
                None,
                f"Hito '{hito.descripcion}' creado.",
                fecha or self._ahora(),
            )

        return hito

    def actualizarHito(
        self,
        idHito,
        descripcion=None,
        fechaCompromiso=None,
        orden=None,
        estado=None,
        fecha=None,
    ):
        sesion, hito, ticket = self._hitoConAcceso(idHito)

        if descripcion is not None:
            hito.descripcion = validarTextoObligatorio(
                descripcion,
                "descripcion",
            )
        if fechaCompromiso is not None:
            if not isinstance(fechaCompromiso, datetime):
                raise ErrorValidacion(
                    "El campo 'fechaCompromiso' debe ser una fecha válida."
                )
            if fechaCompromiso < ticket.fechaCreacion:
                raise ErrorValidacion(
                    "La fecha de compromiso no puede ser anterior a la "
                    "creación del ticket."
                )
            hito.fechaCompromiso = fechaCompromiso
        if orden is not None:
            hito.orden = validarEnteroPositivo(orden, "orden")
            if any(
                otro.idHito != hito.idHito and otro.orden == hito.orden
                for otro in self.repositorioHitos.listarPorTicket(
                    hito.idTicket
                )
            ):
                raise ErrorConflicto(
                    "Ya existe un hito con ese orden en el ticket."
                )
        if estado is not None:
            hito.actualizarEstado(estado)

        with transaccion(self.conexion):
            self.repositorioHitos.actualizar(hito)
            self.repositorioHistorial.insertar(
                hito.idTicket,
                sesion.idUsuario,
                "HITO_ACTUALIZADO",
                None,
                None,
                f"Hito '{hito.descripcion}' actualizado.",
                fecha or self._ahora(),
            )

        return hito

    def completarHito(self, idHito, fecha=None):
        sesion, hito, ticket = self._hitoConAcceso(idHito)

        if hito.estado == ESTADO_HITO_CUMPLIDO:
            raise ErrorEstado("El hito ya está cumplido.")

        momento = fecha or self._ahora()
        hito.completar(momento)

        with transaccion(self.conexion):
            self.repositorioHitos.actualizar(hito)
            self.repositorioHistorial.insertar(
                hito.idTicket,
                sesion.idUsuario,
                "HITO_CUMPLIDO",
                None,
                None,
                f"Hito '{hito.descripcion}' cumplido.",
                momento,
            )

        hitos = self.repositorioHitos.listarPorTicket(ticket.idTicket)
        if (
            hitos
            and all(
                actual.estado == ESTADO_HITO_CUMPLIDO
                for actual in hitos
            )
            and ticket.estado == ESTADO_EN_PROGRESO
        ):
            self.controlTicket.cambiarEstado(
                ticket.idTicket,
                EVENTO_RESOLVER,
                momento,
            )

        return hito

    def listarHitos(self, idTicket):
        self._ticketConAcceso(idTicket)
        return self.repositorioHitos.listarPorTicket(idTicket)

    def verificarVencidos(self, hoy=None):
        sesion = self.controlUsuario.requerirRol(ROL_REPRESENTANTE)

        referencia = hoy or self._ahora()
        if not isinstance(referencia, datetime):
            raise ErrorValidacion(
                "La fecha de referencia debe ser una fecha válida."
            )

        vencidos = []
        with transaccion(self.conexion):
            for hito in self.repositorioHitos.listarVencidos(referencia):
                if hito.estado == ESTADO_HITO_VENCIDO:
                    continue

                ticket = self.repositorioTickets.buscarPorId(
                    hito.idTicket
                )
                if ticket is None:
                    continue

                hito.actualizarEstado(ESTADO_HITO_VENCIDO)
                self.repositorioHitos.actualizar(hito)
                self.repositorioHistorial.insertar(
                    hito.idTicket,
                    sesion.idUsuario,
                    "HITO_VENCIDO",
                    None,
                    None,
                    f"Hito '{hito.descripcion}' vencido.",
                    referencia,
                )
                self.controlNotificaciones.notificarHitoVencido(
                    ticket,
                    hito,
                )
                vencidos.append(hito)

        return vencidos

    def _ticketParaRepresentante(self, idTicket):
        sesion = self.controlUsuario.requerirRol(ROL_REPRESENTANTE)

        ticket = self.repositorioTickets.buscarPorId(idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")
        if ticket.idRepresentante != sesion.idUsuario:
            raise ErrorPermiso(
                "No tiene permiso para modificar este ticket."
            )
        if ticket.estado == ESTADO_CERRADO:
            raise ErrorEstado("El ticket está cerrado.")

        return sesion, ticket

    def _hitoConAcceso(self, idHito):
        _, hito, ticket = self._hitoYticket(idHito)
        sesion = self.controlUsuario.requerirRol(ROL_REPRESENTANTE)

        if ticket.idRepresentante != sesion.idUsuario:
            raise ErrorPermiso(
                "No tiene permiso para modificar este ticket."
            )
        if ticket.estado == ESTADO_CERRADO:
            raise ErrorEstado("El ticket está cerrado.")

        return sesion, hito, ticket

    def _hitoYticket(self, idHito):
        hito = self.repositorioHitos.buscarPorId(idHito)
        if hito is None:
            raise ErrorNoEncontrado("El hito indicado no existe.")

        ticket = self.repositorioTickets.buscarPorId(hito.idTicket)
        if ticket is None:
            raise ErrorNoEncontrado("El ticket indicado no existe.")

        return self.controlUsuario.requerirSesion(), hito, ticket

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
