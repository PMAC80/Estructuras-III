class Cliente:
    def __init__(self, nombre, tiempo_espera):
        self.nombre = nombre
        self.tiempo_espera = tiempo_espera  # Tiempo simulado en minutos
        self.siguiente = None

class SistemaTurnos:
    def __init__(self):
        self.frente = None
        self.final = None

    def registrar_cliente(self, nombre, tiempo_espera):
        nuevo_cliente = Cliente(nombre, tiempo_espera)
        if self.final is None:
            self.frente = nuevo_cliente
            self.final = nuevo_cliente
        else:
            self.final.siguiente = nuevo_cliente
            self.final = nuevo_cliente
        print(f"Registrado: {nombre}")

    def mostrar_orden_llegada(self):
        print("\n--- Lista de Espera (Orden de Llegada) ---")
        actual = self.frente
        if actual is None:
            print("No hay clientes en espera.")
        while actual:
            print(f"- {actual.nombre}")
            actual = actual.siguiente

    def llamar_proximo(self, box_nro):
        if self.frente is None:
            print(f"\n[Box {box_nro}] No hay clientes en espera.")
            return

        cliente_llamado = self.frente
        self.frente = self.frente.siguiente
        
        # Si se vació la cola
        if self.frente is None:
            self.final = None
            
        print(f"\n>>> PRÓXIMO CLIENTE: {cliente_llamado.nombre} – Atendido en Box Nro: {box_nro} <<<")

    # --- IMPLEMENTACIÓN RECURSIVA ---
    def imprimir_tiempos_espera(self):
        print("\n--- Tiempos de Espera (Impresión Recursiva) ---")
        if self.frente is None:
            print("Lista vacía.")
        else:
            self._imprimir_recursivo(self.frente)

    def _imprimir_recursivo(self, nodo_actual):
        # Caso Base: Si el nodo actual es nulo, terminamos la recursividad
        if nodo_actual is None:
            return
        
        # Procesamiento: Imprimimos la información del cliente actual
        print(f"Cliente: {nodo_actual.nombre} | Tiempo de espera: {nodo_actual.tiempo_espera} minutos")
        
        # Llamada Recursiva: Pasamos al siguiente cliente de la cola
        self._imprimir_recursivo(nodo_actual.siguiente)


# Ejecución de prueba
if __name__ == "__main__":
    sistema = SistemaTurnos()

    # 1. Registrar clientes
    sistema.registrar_cliente("Ana Perez", 15)
    sistema.registrar_cliente("Carlos Gomez", 10)
    sistema.registrar_cliente("Maria Lopez", 25)
    sistema.registrar_cliente("Juan Diaz", 5)

    # 2. Mostrar orden de llegada
    sistema.mostrar_orden_llegada()

    # 3. Imprimir el tiempo de espera (RECURSIVO)
    sistema.imprimir_tiempos_espera()

    # 4. Llamar por pantalla
    sistema.llamar_proximo(box_nro=1)
    sistema.llamar_proximo(box_nro=3)

    # Mostrar tiempos y lista otra vez para verificar que la cola avanzó
    sistema.mostrar_orden_llegada()
    sistema.imprimir_tiempos_espera()
