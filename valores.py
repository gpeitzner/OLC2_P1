class Valor:
    'Clase Abstracta'


class Entero(Valor):
    def __init__(self, valor):
        self.valor = valor


class Cadena(Valor):
    def __init__(self, valor):
        self.valor = valor


class Caracter(Valor):
    def __init__(self, valor):
        self.valor = valor


class Decimal(Valor):
    def __init__(self, valor):
        self.valor = valor


class Registro(Valor):
    def __init__(self, registro):
        self.registro = registro


class RegistroArreglo(Valor):
    def __init__(self, registro, accesos):
        self.registro = registro
        self.accesos = accesos


class Arreglo(Valor):
    def __init__(self, valor):
        self.valor = valor
