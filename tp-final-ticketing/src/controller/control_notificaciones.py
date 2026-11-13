from datetime import datetime, timedelta

from src.db.conexion import transaccion
from src.excepciones import (
    ErrorNoEncontrado,
    ErrorPermiso,
    ErrorValidacion,
)
from src.models.estados import (
    PRIORIDAD_ALTA,
    PRIORIDAD_MEDIA,
    PRIORIDADES,
)
from src.models.validaciones import (
    validarTextoObligatorio,
)

HORAS_TICKET_SIN_ASIGNAR = 24


class ControlNotificaciones:
    def __init__(
        self,
        conexion,
        repositorioAlertas,
        repositorioTickets,
        repositorioUsuarios,
        repositorioRepresentantes,
        controlUsuario,
        reloj=None,
    ):
        self.conexion = conexion
        self.repositorioAlertas = repositorioAlertas
        self.repositorioTickets = repositorioTickets
        self.repositorioUsuarios = repositorioUsuarios
        self.repositorioRepresentantes = repositorioRepresentantes
        self.controlUsuario = controlUsuario
        self.reloj = reloj or datetime.now

    def _ahora(self):
        return self.reloj()

    def generarAlerta(
        self,
        idUsuario,
        idTicket,
        tipo,
        prioridad,
        mensaje,
        fecha=None,
    ):
        if prioridad not in PRIORIDADES:
            raise ErrorValidacion("La prioridad de la alerta no es válida.")
        tipo = validarTextoObligatorio(tipo, "tipo")
        mensaje = validarTextoObligatorio(mensaje, "mensaje")

        if self.repositorioUsuarios.buscarPorId(idUsuario) is None:
            raise ErrorNoEncontrado(
                "El usuario destinatario de la alerta no existe."
            )
        if (
            idTicket is not None
            and self.repositorioTickets.buscarPorId(idTicket) is None
        ):
            raise ErrorNoEncontrado("El ticket de la alerta no existe.")

        return self.repositorioAlertas.insertar(
            idUsuario,
            idTicket,
            tipo,
            prioridad,
            mensaje,
            fechaCreacion=fecha or self._ahora(),
        )

    def listarAlertas(self, soloPendientes=True):
        sesion = self.controlUsuario.requerirSesion()
        return self.repositorioAlertas.listarPorUsuario(
            sesion.idUsuario,
            soloPendientes,
        )

    def listarAlertasDeUsuario(self, idUsuario, soloPendientes=True):
        sesion = self.controlUsuario.requerirSesion()
        if sesion.idUsuario != idUsuario:
            raise ErrorPermiso(
                "No puede consultar las alertas de otro usuario."
            )
        return self.repositorioAlertas.listarPorUsuario(
            idUsuario,
            soloPendientes,
        )

    def listarAlertasDeRol(self, rol, soloPendientes=True):
        sesion = self.controlUsuario.requerirSesion()
        if sesion.rol != rol:
            raise ErrorPermiso(
                "No puede consultar las alertas de otro rol."
            )

        alertas = []
        for usuario in self.repositorioUsuarios.listarPorRol(rol):
            alertas.extend(
                self.repositorioAlertas.listarPorUsuario(
                    usuario.idUsuario,
                    soloPendientes,
                )
            )
        alertas.sort(
            key=lambda alerta: (alerta.fechaCreacion, alerta.idAlerta),
            reverse=True,
        )
        return alertas

    def marcarLeida(self, idAlerta):
        sesion = self.controlUsuario.requerirSesion()
        alerta = self.repositorioAlertas.buscarPorId(idAlerta)
        if alerta is None:
            raise ErrorNoEncontrado("La alerta indicada no existe.")
        if alerta.idUsuario != sesion.idUsuario:
            raise ErrorPermiso("No puede modificar una alerta ajena.")

        self.repositorioAlertas.marcarLeida(idAlerta)
        return self.repositorioAlertas.buscarPorId(idAlerta)

    def notificarCambioEstado(
        self,
        ticket,
        estadoAnterior,
        estadoNuevo,
        idDestinatario=None,
    ):
        destinatario = idDestinatario or ticket.idCliente
        mensaje = (
            f"El ticket #{ticket.idTicket} cambió de "
            f"{estadoAnterior} a {estadoNuevo}."
        )
        return self.generarAlerta(
            destinatario,
            ticket.idTicket,
            "CAMBIO_ESTADO",
            PRIORIDAD_MEDIA,
            mensaje,
        )

    def notificarMensaje(self, idTicket, idDestinatario):
        return self.generarAlerta(
            idDestinatario,
            idTicket,
            "MENSAJE_NUEVO",
            PRIORIDAD_MEDIA,
            f"Nuevo mensaje en el ticket #{idTicket}.",
        )

    def notificarReapertura(self, ticket, motivo):
        mensaje = (
            f"El ticket #{ticket.idTicket} fue reabierto: {motivo}"
        )
        return [
            self.generarAlerta(
                idDestinatario,
                ticket.idTicket,
                "REAPERTURA",
                PRIORIDAD_ALTA,
                mensaje,
            )
            for idDestinatario in self._destinatariosRepresentantes(ticket)
        ]

    def notificarHitoVencido(self, ticket, hito):
        mensaje = (
            f"El hito '{hito.descripcion}' del ticket "
            f"#{ticket.idTicket} está vencido."
        )
        return [
            self.generarAlerta(
                idDestinatario,
                ticket.idTicket,
                "HITO_VENCIDO",
                PRIORIDAD_ALTA,
                mensaje,
            )
            for idDestinatario in self._destinatariosRepresentantes(ticket)
        ]

    def notificarTicketSinAsignar(self, ticket, fecha=None):
        mensaje = (
            f"El ticket #{ticket.idTicket} lleva más de "
            f"{HORAS_TICKET_SIN_ASIGNAR} horas sin asignar."
        )
        return [
            self.generarAlerta(
                representante.idUsuario,
                ticket.idTicket,
                "TICKET_SIN_ASIGNAR",
                PRIORIDAD_ALTA,
                mensaje,
                fecha,
            )
            for representante in self.repositorioRepresentantes.listarActivos()
        ]

    def verificarTicketsSinAsignar(self, ahora=None):
        referencia = ahora or self._ahora()
        ids_alertas = []

        with transaccion(self.conexion):
            for ticket in self.repositorioTickets.listarSinAsignar():
                antiguedad = referencia - ticket.fechaCreacion
                if antiguedad > timedelta(
                    hours=HORAS_TICKET_SIN_ASIGNAR
                ):
                    ids_alertas.extend(
                        self.notificarTicketSinAsignar(ticket, referencia)
                    )

        return ids_alertas

    def _destinatariosRepresentantes(self, ticket):
        if ticket.idRepresentante is not None:
            return [ticket.idRepresentante]
        return [
            representante.idUsuario
            for representante in self.repositorioRepresentantes.listarActivos()
        ]
