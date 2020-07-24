class Instruccion:
    'Clase Abstracta'


class Principal(Instruccion):
    'Principal'


class Etiqueta(Instruccion):
    def __init__(self, etiqueta, linea):
        self.etiqueta = etiqueta
        self.linea = linea


class Salto(Instruccion):
    def __init__(self, etiqueta, linea):
        self.etiqueta = etiqueta
        self.linea = linea


class Asignacion(Instruccion):
    def __init__(self, identificador, expresion, linea):
        self.identificador = identificador
        self.expresion = expresion
        self.linea = linea


class AsignacionArreglo(Instruccion):
    def __init__(self, identificador, accesos, expresion, linea):
        self.identificador = identificador
        self.accesos = accesos
        self.expresion = expresion
        self.linea = linea


class Eliminar(Instruccion):
    def __init__(self, registro, linea):
        self.registro = registro
        self.linea = linea


class Imprimir(Instruccion):
    def __init__(self, expresion, linea):
        self.expresion = expresion
        self.linea = linea


class Si(Instruccion):
    def __init__(self, expresion, etiqueta, linea):
        self.expresion = expresion
        self.etiqueta = etiqueta
        self.linea = linea


class Salir(Instruccion):
    'Salir'
