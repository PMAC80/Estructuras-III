from datetime import datetime

from src.excepciones import ErrorDominio, ErrorValidacion
from src.gui.menus import (
    MENU_CLIENTE,
    MENU_INICIAL,
    MENU_REPRESENTANTE,
)
from src.models.estados import (
    ESTADO_RESUELTO,
    ROL_CLIENTE,
    ROL_REPRESENTANTE,
)


class GUI:
    def __init__(
        self,
        consola,
        controlUsuario,
        controlTicket,
        controlHito,
        controlNotificaciones,
    ):
        self.consola = consola
        self.controlUsuario = controlUsuario
        self.controlTicket = controlTicket
        self.controlHito = controlHito
        self.controlNotificaciones = controlNotificaciones

    def iniciar(self):
        while True:
            sesion = self.controlUsuario.obtenerSesion()
            if sesion is None:
                self.mostrarMenu(
                    "=== Sistema de Ticketing ===",
                    MENU_INICIAL,
                )
                opcion = self._leer("Opción: ")
                if opcion == "1":
                    self._ejecutarSeguro(self.ejecutarRegistro)
                elif opcion == "2":
                    self._ejecutarSeguro(self.ejecutarLogin)
                elif opcion == "3":
                    self.escribir("Hasta luego.")
                    return
                else:
                    self.escribir("Opción inválida.")
            else:
                self._menuSesion(sesion)

    def _menuSesion(self, sesion):
        if sesion.rol == ROL_CLIENTE:
            menu = MENU_CLIENTE
            titulo = "=== Menú Cliente ==="
        elif sesion.rol == ROL_REPRESENTANTE:
            menu = MENU_REPRESENTANTE
            titulo = "=== Menú Representante ==="
        else:
            self.escribir("Rol no reconocido.")
            self.cerrarSesion()
            return

        while self.controlUsuario.obtenerSesion() is not None:
            self.mostrarMenu(titulo, menu)
            opcion = self._leer("Opción: ")
            if opcion == "0":
                self.cerrarSesion()
                return
            self._despachar(sesion.rol, opcion)

    def _despachar(self, rol, opcion):
        acciones = {
            ROL_CLIENTE: {
                "1": self.ejecutarCrearTicket,
                "2": self.ejecutarVerTickets,
                "3": self.ejecutarMensajes,
                "4": self.ejecutarGestionHitos,
                "5": self.ejecutarRevisarAlertas,
                "6": self.ejecutarReabrirTicket,
            },
            ROL_REPRESENTANTE: {
                "1": self.ejecutarAsignarTicket,
                "2": self.ejecutarVerTickets,
                "3": self.ejecutarMensajes,
                "4": self.ejecutarGestionHitos,
                "5": self.ejecutarActualizarEstado,
                "6": self.ejecutarCerrarTicket,
                "7": self.ejecutarReabrirTicket,
                "8": self.ejecutarRevisarAlertas,
            },
        }
        accion = acciones.get(rol, {}).get(opcion)
        if accion is None:
            self.escribir("Opción inválida.")
            return
        self._ejecutarSeguro(accion)

    def mostrarMenu(self, titulo, opciones):
        self.escribir(titulo)
        for clave in sorted(opciones):
            self.escribir(f"{clave}. {opciones[clave]}")
        self.escribir()

    def ejecutarRegistro(self):
        nombre = self._leer("Nombre: ")
        email = self._leer("Email: ")
        contrasena = self._leer("Contraseña: ")
        rol_opcion = self._leer(
            "Rol (1=Cliente, 2=Representante): "
        )
        if rol_opcion == "1":
            rol = ROL_CLIENTE
            legajo = None
        elif rol_opcion == "2":
            rol = ROL_REPRESENTANTE
            legajo = self._leer("Legajo: ")
        else:
            raise ErrorValidacion("El rol seleccionado no es válido.")

        self.controlUsuario.registrar(
            nombre,
            email,
            contrasena,
            rol,
            legajo=legajo,
        )
        self.escribir("Registro exitoso. Inicie sesión.")

    def ejecutarLogin(self):
        email = self._leer("Email: ")
        contrasena = self._leer("Contraseña: ")
        sesion = self.controlUsuario.login(email, contrasena)
        self.escribir(f"Bienvenido/a, {sesion.nombre}.")

    def cerrarSesion(self):
        self.controlUsuario.logout()
        self.escribir("Sesión cerrada.")

    def ejecutarCrearTicket(self):
        tipos = self.controlTicket.listarTiposProducto()
        if not tipos:
            self.escribir("No hay tipos de producto disponibles.")
            return

        self.escribir("=== Tipos de producto ===")
        for tipo in tipos:
            self.escribir(
                f"{tipo.idTipoProducto}. {tipo.nombre}"
            )

        idTipo = self._leerEntero("Seleccione tipo de producto: ")
        productos = self.controlTicket.listarProductosDeTipo(idTipo)
        if not productos:
            self.escribir(
                "No hay productos disponibles para ese tipo."
            )
            return

        self.escribir("=== Productos ===")
        for producto in productos:
            self.escribir(
                f"{producto.idProducto}. {producto.getDescripcion()}"
            )

        idProducto = self._leerEntero("Seleccione producto: ")
        titulo = self._leer("Título: ")
        descripcion = self._leer("Descripción: ")
        prioridad = self._leer(
            "Prioridad (ALTA/MEDIA/BAJA): "
        ).upper()

        ticket = self.controlTicket.crearTicket(
            titulo,
            descripcion,
            prioridad,
            idProducto,
            idTipo,
        )
        self.escribir(
            f"Ticket #{ticket.idTicket} creado correctamente."
        )

    def ejecutarVerTickets(self):
        tickets = self.controlTicket.listarTickets()
        self._mostrarTickets(tickets)

    def ejecutarAsignarTicket(self):
        tickets = self.controlTicket.listarTicketsNuevos()
        if not tickets:
            self.escribir("No hay tickets nuevos para asignar.")
            return

        self.escribir("=== Tickets nuevos ===")
        self._mostrarTickets(tickets)
        idTicket = self._leerEntero("Ticket a asignar: ")

        representantes = (
            self.controlTicket.listarRepresentantesActivos()
        )
        if not representantes:
            self.escribir("No hay representantes activos.")
            return

        self.escribir("=== Representantes ===")
        for representante in representantes:
            self.escribir(
                f"{representante.idUsuario}. "
                f"{representante.nombre} "
                f"({representante.legajo or 'sin legajo'})"
            )

        idRepresentante = self._leerEntero(
            "Seleccione representante: "
        )
        self.controlTicket.asignarTicket(
            idTicket,
            idRepresentante,
        )
        nombre = next(
            (
                representante.nombre
                for representante in representantes
                if representante.idUsuario == idRepresentante
            ),
            str(idRepresentante),
        )
        self.escribir(
            f"Ticket #{idTicket} asignado a {nombre}."
        )

    def ejecutarMensajes(self):
        tickets = self.controlTicket.listarTickets()
        if tickets:
            self.escribir("=== Mis tickets ===")
            self._mostrarTickets(tickets)
        else:
            self.escribir("No tiene tickets disponibles.")

        idTicket = self._leerEntero("Ticket: ")
        mensajes = self.controlTicket.listarMensajes(idTicket)
        self._mostrarMensajes(idTicket, mensajes)

        enviar = self._leer("¿Enviar mensaje? (s/n): ").lower()
        if enviar == "s":
            contenido = self._leer("Mensaje: ")
            self.controlTicket.agregarMensaje(idTicket, contenido)
            self.escribir("Mensaje enviado.")
            mensajes = self.controlTicket.listarMensajes(idTicket)
            self.escribir("=== Mensajes actualizados ===")
            self._mostrarMensajes(idTicket, mensajes)

    def ejecutarGestionHitos(self):
        tickets = self.controlTicket.listarTickets()
        if tickets:
            self.escribir("=== Mis tickets ===")
            self._mostrarTickets(tickets)
        else:
            self.escribir("No tiene tickets disponibles.")

        idTicket = self._leerEntero("Ticket: ")
        self._mostrarHitos(idTicket)

        self.escribir("1. Crear hito")
        self.escribir("2. Actualizar hito")
        self.escribir("3. Completar hito")
        self.escribir("0. Volver")
        accion = self._leer("Opción: ")

        if accion == "0":
            return
        if accion == "1":
            descripcion = self._leer("Descripción del hito: ")
            fecha = self._leerFecha(
                "Fecha compromiso (AAAA-MM-DD HH:MM): "
            )
            orden = self._leerEntero("Orden: ")
            self.controlHito.crearHito(
                idTicket,
                descripcion,
                fecha,
                orden=orden,
            )
            self.escribir("Hito creado.")
            return
        if accion == "2":
            idHito = self._leerEntero("Hito a actualizar: ")
            descripcion = self._leer(
                "Descripción (Enter para mantener): "
            )
            fechaTexto = self._leer(
                "Fecha compromiso (AAAA-MM-DD HH:MM, "
                "Enter para mantener): "
            )
            ordenTexto = self._leer(
                "Orden (Enter para mantener): "
            )
            self.controlHito.actualizarHito(
                idHito,
                descripcion=descripcion or None,
                fechaCompromiso=(
                    self._leerFechaDeTexto(fechaTexto)
                    if fechaTexto
                    else None
                ),
                orden=int(ordenTexto) if ordenTexto else None,
            )
            self.escribir("Hito actualizado.")
            return
        if accion == "3":
            idHito = self._leerEntero("Hito a completar: ")
            self.controlHito.completarHito(idHito)
            self.escribir("Hito completado.")
            if self._ticketEstaResuelto(idTicket):
                self.escribir(
                    "El ticket fue resuelto automáticamente."
                )
            return

        self.escribir("Opción inválida.")

    def ejecutarActualizarEstado(self):
        tickets = self.controlTicket.listarTickets()
        if not tickets:
            self.escribir("No tiene tickets asignados.")
            return

        self.escribir("=== Mis tickets ===")
        self._mostrarTickets(tickets)
        idTicket = self._leerEntero("Ticket: ")

        self.escribir("1. Iniciar trabajo")
        self.escribir("2. Resolver")
        opcion = self._leer("Opción: ")
        eventos = {"1": "INICIAR", "2": "RESOLVER"}
        evento = eventos.get(opcion)
        if evento is None:
            self.escribir("Opción inválida.")
            return

        ticket = self.controlTicket.cambiarEstado(idTicket, evento)
        self.escribir(f"Estado actualizado a {ticket.estado}.")

    def ejecutarRevisarAlertas(self):
        alertas = self.controlNotificaciones.listarAlertas()
        if not alertas:
            self.escribir("No hay alertas pendientes.")
            return

        self.escribir("=== Alertas pendientes ===")
        for alerta in alertas:
            self.escribir(
                f"#{alerta.idAlerta} [{alerta.tipo}] "
                f"{alerta.mensaje}"
            )

        texto = self._leer(
            "Marque leída (id o Enter para salir): "
        )
        if texto:
            self.controlNotificaciones.marcarLeida(int(texto))
            self.escribir("Alerta marcada como leída.")

    def ejecutarCerrarTicket(self):
        tickets = self.controlTicket.listarTickets()
        if not tickets:
            self.escribir("No tiene tickets asignados.")
            return

        self.escribir("=== Mis tickets ===")
        self._mostrarTickets(tickets)
        idTicket = self._leerEntero("Ticket a cerrar: ")
        comentario = self._leer("Comentario de cierre: ")

        self.controlTicket.cerrarTicket(
            idTicket,
            comentario or None,
        )
        self.escribir(f"Ticket #{idTicket} cerrado.")

    def ejecutarReabrirTicket(self):
        tickets = self.controlTicket.listarTickets()
        if not tickets:
            self.escribir("No tiene tickets disponibles.")
            return

        self.escribir("=== Mis tickets ===")
        self._mostrarTickets(tickets)
        idTicket = self._leerEntero("Ticket a reabrir: ")
        motivo = self._leer("Motivo de reapertura: ")

        self.controlTicket.reabrirTicket(idTicket, motivo)
        self.escribir(f"Ticket #{idTicket} reabierto.")

    def _mostrarTickets(self, tickets):
        if not tickets:
            self.escribir("No hay tickets.")
            return
        for ticket in tickets:
            self.escribir(
                f"#{ticket.idTicket} [{ticket.estado}] "
                f"{ticket.titulo} - prioridad {ticket.prioridad}"
            )

    def _mostrarMensajes(self, idTicket, mensajes):
        self.escribir(f"=== Mensajes del ticket #{idTicket} ===")
        if not mensajes:
            self.escribir("No hay mensajes.")
            return
        for mensaje in mensajes:
            self.escribir(
                f"#{mensaje.idMensaje} autor {mensaje.idAutor}: "
                f"{mensaje.contenido}"
            )

    def _mostrarHitos(self, idTicket):
        hitos = self.controlHito.listarHitos(idTicket)
        self.escribir(f"=== Hitos del ticket #{idTicket} ===")
        if not hitos:
            self.escribir("No hay hitos.")
            return
        for hito in hitos:
            self.escribir(
                f"#{hito.idHito} [{hito.estado}] "
                f"{hito.descripcion} - orden {hito.orden}"
            )

    def _ticketEstaResuelto(self, idTicket):
        tickets = self.controlTicket.listarTickets()
        return any(
            ticket.idTicket == idTicket
            and ticket.estado == ESTADO_RESUELTO
            for ticket in tickets
        )

    def _leerEntero(self, mensaje):
        texto = self._leer(mensaje)
        try:
            return int(texto)
        except ValueError as error:
            raise ErrorValidacion(
                "Debe ingresar un número válido."
            ) from error

    def _leerFecha(self, mensaje):
        return self._leerFechaDeTexto(self._leer(mensaje))

    def _leerFechaDeTexto(self, texto):
        try:
            return datetime.fromisoformat(texto)
        except ValueError as error:
            raise ErrorValidacion(
                "Formato de fecha inválido. Use AAAA-MM-DD HH:MM."
            ) from error

    def _leer(self, mensaje):
        return self.consola.leer(mensaje).strip()

    def escribir(self, mensaje=""):
        self.consola.escribir(mensaje)

    def _ejecutarSeguro(self, accion):
        try:
            accion()
        except ErrorDominio as error:
            self.escribir(f"Error: {error}")
        except (ValueError, TypeError):
            self.escribir("Entrada inválida.")
        except Exception:
            self.escribir("Ocurrió un error inesperado.")
