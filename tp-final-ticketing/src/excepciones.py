class ErrorDominio(Exception):
    pass


class ErrorValidacion(ErrorDominio):
    pass


class ErrorAutenticacion(ErrorDominio):
    pass


class ErrorPermiso(ErrorDominio):
    pass


class ErrorEstado(ErrorDominio):
    pass


class ErrorNoEncontrado(ErrorDominio):
    pass


class ErrorConflicto(ErrorDominio):
    pass
