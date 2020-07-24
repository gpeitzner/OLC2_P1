class Simbolo():
    def __init__(self, identificador, tipo, valor):
        self.identificador = identificador
        self.tipo = tipo
        self.valor = valor


class TablaSimbolos():
    def __init__(self, simbolos={}):
        self.simbolos = simbolos

    def agregar(self, simbolo):
        self.simbolos[simbolo.identificador] = simbolo

    def obtener(self, identificador):
        if identificador in self.simbolos:
            return self.simbolos[identificador]

    def actualizar(self, simbolo):
        if simbolo.identificador in self.simbolos:
            self.simbolos[simbolo.identificador] = simbolo

    def eliminar(self, identificador):
        if not identificador in self.simbolos:
            return False
        else:
            del self.simbolos[identificador]
            return True
