class Consola:
    def leer(self, mensaje=""):
        raise NotImplementedError

    def escribir(self, mensaje=""):
        raise NotImplementedError


class ConsolaReal(Consola):
    def leer(self, mensaje=""):
        return input(mensaje)

    def escribir(self, mensaje=""):
        print(mensaje)
