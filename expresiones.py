class Expresion:
    'Clase Abstracta'


class OperacionAritmetica(Expresion):
    def __init__(self, primerOperando, operacion, segundoOperando):
        self.primerOperando = primerOperando
        self.operacion = operacion
        self.segundoOperando = segundoOperando


class OperacionLogica(Expresion):
    def __init__(self, primerOperando, operacion, segundoOperando):
        self.primerOperando = primerOperando
        self.operacion = operacion
        self.segundoOperando = segundoOperando


class OperacionBit(Expresion):
    def __init__(self, primerOperando, operacion, segundoOperando):
        self.primerOperando = primerOperando
        self.operacion = operacion
        self.segundoOperando = segundoOperando


class OperacionRelacional(Expresion):
    def __init__(self, primerOperando, operacion, segundoOperando):
        self.primerOperando = primerOperando
        self.operacion = operacion
        self.segundoOperando = segundoOperando


class OperacionUnaria(Expresion):
    def __init__(self, operacion, operando):
        self.operacion = operacion
        self.operando = operando


class OperacionFuncion(Expresion):
    def __init__(self, funcion, operando):
        self.funcion = funcion
        self.operando = operando


class OperacionCasteo(Expresion):
    def __init__(self, tipo, operando):
        self.tipo = tipo
        self.operando = operando
