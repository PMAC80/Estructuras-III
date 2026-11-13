# Matriz de aceptación — Sistema de Ticketing

Fecha de verificación: 2026-11-10

## Resultado general

- Suite completa: **256 tests en verde**.
- Cobertura total de `src`: **94%**.
- Cobertura de controladores: **90%–97%**.
- Cobertura de modelos: **92%–100%**.
- Sin imports prohibidos entre capas.
- Sin dependencias externas de runtime.

## RF1 — Registro de usuarios

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Registro válido crea el usuario y permite iniciar sesión | `tests/integration/test_control_usuario.py::test_registrarClientePersisteUsuarioYPerfil` |
| Registro de representante persiste su perfil | `tests/integration/test_control_usuario.py::test_registrarRepresentantePersistePerfil` |
| Registro desde la GUI | `tests/e2e/test_gui_auth_menus.py::test_registroYLoginDesdeLaGui` |
| Email duplicado rechazado con mensaje claro | `tests/integration/test_control_usuario.py::test_registrarEmailDuplicadoLanzaConflicto` |
| Contraseña hasheada con salt, nunca en texto plano | `tests/unit/test_seguridad.py::test_generarHash_noAlmacenaContrasenaEnTextoPlano` |
| El modelo rechaza contraseñas en texto plano | `tests/unit/test_usuario.py::test_constructor_rechazaContrasenaEnTextoPlano` |
| Ciclo completo RF1 | `tests/e2e/test_flujo_completo.py::test_flujoE2ECompletoRf1Rf10` |

## RF2 — Login y sesión

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Credenciales correctas crean sesión | `tests/integration/test_control_usuario.py::test_loginValidoCreaSesion` |
| Credenciales incorrectas no crean sesión | `tests/integration/test_control_usuario.py::test_loginCredencialesInvalidasNoCreanSesion` |
| Error genérico en GUI sin revelar el dato incorrecto | `tests/e2e/test_gui_auth_menus.py::test_loginConCredencialesInvalidasMuestraErrorYNoCreaSesion` |
| Usuario inactivo rechazado | `tests/integration/test_control_usuario.py::test_loginUsuarioInactivoLanzaAutenticacion` |
| Logout elimina la sesión | `tests/integration/test_control_usuario.py::test_logoutEliminaSesion` |
| Tras logout se vuelve al menú inicial | `tests/e2e/test_gui_auth_menus.py::test_menuClienteMuestraSoloOpcionesDelClienteYLogoutVuelveAlInicio` |
| Operaciones sin sesión rechazadas | `tests/integration/test_control_usuario.py::test_requerirRolSinSesionLanzaAutenticacion` |

## RF3 — Crear ticket

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Ticket válido se guarda en `NUEVO` con cliente correcto | `tests/integration/test_control_ticket_creacion.py::test_crearTicketValidoRegistraEstadoClienteEHistorial` |
| Datos obligatorios inválidos impiden la creación | `tests/integration/test_control_ticket_creacion.py::test_crearTicketConDatosInvalidosLanzaValidacion` |
| Producto de otro tipo rechazado | `tests/integration/test_control_ticket_creacion.py::test_crearTicketConProductoDeOtroTipoLanzaValidacion` |
| Creación desde la GUI muestra el identificador | `tests/e2e/test_gui_tickets.py::test_flujoCrearTicketMuestraIdentificadorYPersiste` |
| Todo ticket creado genera historial | `tests/integration/test_control_ticket_creacion.py::test_crearTicketValidoRegistraEstadoClienteEHistorial` |

## RF4 — Asignar ticket

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Asignar un ticket `NUEVO` lo pasa a `ASIGNADO` | `tests/integration/test_control_ticket_asignacion_estado.py::test_asignarTicketValidoActualizaEstadoHistorialYAlerta` |
| Asignación a representante inactivo rechazada | `tests/integration/test_control_ticket_asignacion_estado.py::test_asignarTicketARepresentanteInactivoLanzaEstado` |
| Ticket `CERRADO` no se asigna | `tests/integration/test_control_ticket_asignacion_estado.py::test_asignarTicketEnEstadoInvalidoLanzaEstado` |
| Ticket `REABIERTO` puede asignarse | `tests/integration/test_control_ticket_asignacion_estado.py::test_asignarTicketReabiertoCambiaAAsignado` |
| La operación registra actor, fecha y alerta | `tests/integration/test_control_ticket_asignacion_estado.py::test_asignarTicketValidoActualizaEstadoHistorialYAlerta` |
| Asignación desde la GUI | `tests/e2e/test_gui_tickets.py::test_flujoAsignarTicketListaNuevosYConfirma` |

## RF5 — Comunicación (mensajes)

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Mensaje válido se guarda y es visible para ambas partes | `tests/integration/test_control_ticket_mensajes_consultas.py::test_agregarMensajeDeClientePersisteHistorialYAlerta` |
| Usuario ajeno no puede enviar mensajes | `tests/integration/test_control_ticket_mensajes_consultas.py::test_agregarMensajeUsuarioAjenoLanzaPermiso` |
| Mensaje aparece en historial con fecha y autor | `tests/integration/test_control_ticket_mensajes_consultas.py::test_agregarMensajeDeClientePersisteHistorialYAlerta` |
| No se permiten mensajes en ticket `CERRADO` | `tests/integration/test_control_ticket_mensajes_consultas.py::test_agregarMensajeATicketCerradoLanzaEstado` |
| Envío y visualización desde la GUI | `tests/e2e/test_gui_tickets.py::test_flujoMensajesPermiteEnviarYVisualizar` |
| Error de acceso ajeno en la GUI | `tests/e2e/test_gui_tickets.py::test_flujoMensajesMuestraErrorDeAccesoAjeno` |

## RF6 — Hitos

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Crear hito refleja estado `PENDIENTE` e historial | `tests/integration/test_control_hito.py::test_crearHitoValidoPersisteYRegistraHistorial` |
| Actualizar hito persiste cambios e historial | `tests/integration/test_control_hito.py::test_actualizarHitoPersisteYRegistraHistorial` |
| Completar todos los hitos resuelve el ticket | `tests/integration/test_control_hito.py::test_completarUltimoHitoResuelveTicket` |
| Hito vencido reportado con alerta | `tests/integration/test_control_hito_vencidos.py::test_verificarVencidosMarcaHitoYGeneraAlerta` |
| Alta de hito desde la GUI | `tests/e2e/test_gui_tickets.py::test_flujoHitosPermiteCrearHito` |
| Actualización de hito desde la GUI | `tests/e2e/test_gui_tickets.py::test_flujoHitosPermiteActualizarHito` |
| Completar hitos resuelve el ticket desde la GUI | `tests/e2e/test_gui_tickets.py::test_flujoCompletarHitosResuelveTicket` |

## RF7 — Historial

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Cada operación relevante produce una entrada | `tests/e2e/test_flujo_completo.py::test_flujoE2ECompletoRf1Rf10` |
| Consulta en orden cronológico | `tests/integration/test_repositorio_historial.py::test_insertarYListarHistorialEnOrdenCronologico` |
| Historial de ticket en orden cronológico | `tests/integration/test_control_ticket_mensajes_consultas.py::test_obtenerHistorialEnOrdenCronologico` |
| Historial inmutable desde repositorio | `tests/integration/test_repositorio_historial.py::test_historialNoExponeOperacionesDeModificacion` |
| Historial no alterable desde la GUI | `tests/e2e/test_flujo_completo.py::test_flujoE2ECompletoRf1Rf10` |

## RF8 — Alertas y notificaciones

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Cambio de estado genera alerta al cliente | `tests/integration/test_control_notificaciones.py::test_notificarCambioEstadoGeneraAlertaAlCliente` |
| Mensaje nuevo genera alerta al destinatario | `tests/integration/test_control_notificaciones.py::test_notificarMensajeGeneraAlertaAlDestinatario` |
| Reapertura genera alerta al representante | `tests/integration/test_control_notificaciones.py::test_notificarReaperturaAlRepresentanteAsignado` |
| Hito vencido genera alerta | `tests/integration/test_control_notificaciones.py::test_notificarHitoVencidoAlRepresentante` |
| Ticket sin asignar más de 24 h genera alerta | `tests/integration/test_control_notificaciones.py::test_verificarTicketsSinAsignarGeneraAlertaTras24h` |
| Lista sólo alertas del usuario actual | `tests/integration/test_control_notificaciones.py::test_listarAlertasDelUsuarioActual` |
| Lista alertas por rol destinatario | `tests/integration/test_control_notificaciones.py::test_listarAlertasPorRol` |
| Marcar leída no elimina la alerta | `tests/integration/test_control_notificaciones.py::test_marcarLeidaNoEliminaYValidaPropietario` |
| Listado, detalle y marcado desde la GUI | `tests/e2e/test_gui_alertas_cierre.py::test_flujoAlertasListaDetalleMarcaLeidaYDetectaSinAlertas` |

## RF9 — Cierre de ticket

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Cerrar ticket `RESUELTO` con hitos cumplidos actualiza estado y fecha | `tests/integration/test_control_ticket_cierre_reapertura.py::test_representanteCierraTicketResueltoConHitosCumplidos` |
| Cerrar ticket no `RESUELTO` es rechazado | `tests/integration/test_control_ticket_cierre_reapertura.py::test_cerrarTicketNoResueltoLanzaEstado` |
| Cierre con hitos pendientes exige justificación | `tests/integration/test_control_ticket_cierre_reapertura.py::test_cerrarConHitosPendientesSinJustificacionLanzaEstado` |
| Cierre sin hitos exige justificación | `tests/integration/test_control_ticket_cierre_reapertura.py::test_cerrarSinHitosRequiereJustificacion` |
| Tras el cierre no se aceptan mensajes ni hitos | `tests/integration/test_control_ticket_cierre_reapertura.py::test_cerrarTicketBloqueaMensajesYHitosPosteriores` |
| Cierre desde la GUI | `tests/e2e/test_gui_alertas_cierre.py::test_flujoCierreYReaperturaDesdeLaGui` |
| Bloqueo de operaciones tras el cierre en la GUI | `tests/e2e/test_gui_alertas_cierre.py::test_ticketCerradoBloqueaMensajesYHitosEnLaGui` |

## RF10 — Reapertura de ticket

| Criterio de aceptación | Test que lo cubre |
|---|---|
| Cliente propietario reabre dentro del plazo y se desasigna | `tests/integration/test_control_ticket_cierre_reapertura.py::test_reabrirTicketPorClienteDentroDelPlazoDesasignaYAlerta` |
| Representante asignado puede reabrir | `tests/integration/test_control_ticket_cierre_reapertura.py::test_reabrirTicketPorRepresentanteAsignado` |
| Reabrir sin motivo es rechazado | `tests/integration/test_control_ticket_cierre_reapertura.py::test_reabrirTicketValidaPermisosMotivoYExistencia` |
| Fuera del plazo de 7 días es rechazado | `tests/integration/test_control_ticket_cierre_reapertura.py::test_reabrirTicketFueraDelPlazoLanzaEstado` |
| Ticket reabierto permite nueva asignación | `tests/integration/test_control_ticket_cierre_reapertura.py::test_reabrirTicketLuegoPuedeAsignarse` |
| Reapertura desde la GUI | `tests/e2e/test_gui_alertas_cierre.py::test_flujoCierreYReaperturaDesdeLaGui` |
| Ciclo completo incluyendo nueva asignación | `tests/e2e/test_flujo_completo.py::test_flujoE2ECompletoRf1Rf10` |

## Casos de uso

| Caso | Test E2E |
|---|---|
| C-1 Login | `tests/e2e/test_gui_auth_menus.py::test_registroYLoginDesdeLaGui` |
| C-1 Login inválido | `tests/e2e/test_gui_auth_menus.py::test_loginConCredencialesInvalidasMuestraErrorYNoCreaSesion` |
| C-2 Crear ticket | `tests/e2e/test_gui_tickets.py::test_flujoCrearTicketMuestraIdentificadorYPersiste` |
| C-3 Revisar alertas | `tests/e2e/test_gui_alertas_cierre.py::test_flujoAlertasListaDetalleMarcaLeidaYDetectaSinAlertas` |

## Requisitos no funcionales y Definition of Done

| Criterio | Verificación |
|---|---|
| Sin imports prohibidos entre capas | `tests/architecture/test_capas.py::test_no_hay_imports_prohibidos_entre_capas` |
| El detector de capas falla ante imports prohibidos | `tests/architecture/test_capas.py::test_detector_reporta_un_import_prohibido` |
| Nomenclatura PascalCase/camelCase | `tests/unit/test_nomenclatura.py::test_clasesYMetodosRespetanLaNomenclaturaDelProyecto` |
| Menús y textos de interfaz en español | `tests/unit/test_nomenclatura.py::test_menusYTextosDeInterfazEstanEnEspanol` |
| Contraseñas hasheadas con salt | `tests/unit/test_seguridad.py::test_generarHash_usaSaltAleatorio` |
| Historial inmutable | `tests/integration/test_repositorio_historial.py::test_historialNoExponeOperacionesDeModificacion` |
| Máquina de estados respetada | `tests/unit/test_ticket_estados.py::test_transiciones_permitidas_recorrenCicloCompleto` |
| Transiciones prohibidas rechazadas | `tests/unit/test_ticket_estados.py::test_transiciones_prohibidas_lanzanErrorEstado[NUEVO-CERRAR]` |
| Integridad referencial activa | `tests/integration/test_conexion.py::test_abrirConexion_configuraRowFactoryYForeignKeys` |
| Carga inicial idempotente | `tests/integration/test_datos_iniciales.py::test_cargaInicialEsIdempotenteYPersiste` |
| Aplicación arranca con DB temporal | `tests/e2e/test_main.py::test_crearAplicacionConBaseTemporalCargaDatosYArranca` |
| Suite completa sin fallos | `256 passed` |
| Cobertura de módulos de negocio | `94%` total; controladores `90%–97%`; modelos `92%–100%` |
| Sin dependencias externas de runtime | `pyproject.toml` sólo declara stdlib y herramientas de desarrollo opcionales |
