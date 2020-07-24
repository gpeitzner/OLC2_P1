from instrucciones import *
from expresiones import *
from valores import *
from graphviz import Digraph
from tablaSimbolos import TablaSimbolos, Simbolo
from ambito import Ambito
import copy
import sys
import time
import re

from PyQt5 import QtWidgets, QtGui


class Interprete():

    def __init__(self, consola):
        self.identificadorNodo = 1
        self.ambitos = []
        self.tablaSimbolos = TablaSimbolos()
        self.detenerEjecucion = False
        self.consola = consola
        sys.setrecursionlimit(5000)

    def cargarParametrosInicio(self):
        self.identificadorNodo = 1
        self.ambitos = []
        self.tablaSimbolos = TablaSimbolos()
        self.tablaSimbolos.simbolos = {}
        self.detenerEjecucion = False

    def obtenerAmbitos(self, ast):
        indiceInstrucciones = 0
        totalInstrucciones = len(ast)
        indicesEtiquetas = []
        while indiceInstrucciones < totalInstrucciones:
            if isinstance(ast[indiceInstrucciones], Etiqueta) or isinstance(ast[indiceInstrucciones], Principal):
                indicesEtiquetas.append(indiceInstrucciones)
            indiceInstrucciones += 1
        indiceAmbitos = 0
        totalAmbitos = len(indicesEtiquetas)
        while indiceAmbitos < totalAmbitos and not self.detenerEjecucion:
            inicioAmbito = indicesEtiquetas[indiceAmbitos]
            if isinstance(ast[inicioAmbito], Principal):
                ambitoEtiqueta = "main"
            else:
                ambitoEtiqueta = ast[inicioAmbito].etiqueta
            ambitoInstrucciones = []
            inicioAmbito += 1
            while inicioAmbito < totalInstrucciones:
                ambitoInstrucciones.append(ast[inicioAmbito])
                inicioAmbito += 1
            nuevoAmbito = Ambito(ambitoEtiqueta, ambitoInstrucciones)
            for ambito in self.ambitos:
                if(nuevoAmbito.etiqueta == ambito.etiqueta):
                    self.mostrarError(
                        "ERROR: Semántico, etiqueta: "+nuevoAmbito.etiqueta+" duplicada.")
                    self.detenerEjecucion = True
            if not self.detenerEjecucion:
                self.ambitos.append(nuevoAmbito)
            indiceAmbitos += 1

    def procesar(self, ast):
        self.cargarParametrosInicio()
        self.obtenerAmbitos(ast)
        if not self.detenerEjecucion:
            self.ejecutar(self.ambitos[0])

    def mostrarDetalles(self):
        print("Ambitos: %d" % len(self.ambitos))
        print("Simbolos: %d" % len(self.tablaSimbolos.simbolos))
        for llave in self.tablaSimbolos.simbolos.keys():
            simbolo = self.tablaSimbolos.simbolos[llave]
            print("ID: "+str(simbolo.identificador)+" Tipo: " +
                  str(simbolo.tipo)+" Valor: "+str(simbolo.valor))
        print("")

    def ejecutar(self, ambito):
        for instruccionTemporal in ambito.instrucciones:
            instruccion = copy.deepcopy(instruccionTemporal)
            if isinstance(instruccion, Principal):
                pass
            elif isinstance(instruccion, Etiqueta):
                pass
            elif isinstance(instruccion, Salto):
                existeAmbito = False
                for ambitoAuxiliar in self.ambitos:
                    if str(ambitoAuxiliar.etiqueta) == str(instruccion.etiqueta):
                        self.ejecutar(ambitoAuxiliar)
                        existeAmbito = True
                if not existeAmbito:
                    self.mostrarError("ERROR: Semántico en línea: "+instruccion.linea +
                                      ", la etiqueta: "+instruccion.etiqueta+" no existe.")
                    self.detenerEjecucion = True
                break
            elif isinstance(instruccion, Asignacion):
                self.ejecutarAsignacion(instruccion)
            elif isinstance(instruccion, AsignacionArreglo):
                self.ejecutarAsignacionArreglo(instruccion)
            elif isinstance(instruccion, Eliminar):
                if not self.tablaSimbolos.eliminar(instruccion.registro):
                    self.mostrarError("ERROR: Semántico en línea: "+instruccion.linea +
                                      ", el registro: "+instruccion.registro+" no existe.")
                    self.detenerEjecucion = True
            elif isinstance(instruccion, Imprimir):
                valor = self.ejecutarExpresion(instruccion.expresion)
                if valor:
                    if isinstance(valor, Cadena):
                        if valor.valor == "\\n":
                            self.consola.setPlainText(
                                self.consola.toPlainText()+"\n")
                        else:
                            self.consola.setPlainText(
                                self.consola.toPlainText()+str(valor.valor))
                    else:
                        if isinstance(valor, Arreglo):
                            self.mostrarError(
                                "ERROR: Semántico en línea: "+instruccion.linea+", la expresión no es válida.")
                            self.detenerEjecucion = True
                        else:
                            self.consola.setPlainText(
                                self.consola.toPlainText()+str(valor.valor))
                    cursorTemporal = self.consola.textCursor()
                    cursorTemporal.setPosition(len(self.consola.toPlainText()))
                    self.consola.setTextCursor(cursorTemporal)
                else:
                    self.mostrarError(
                        "ERROR: Semántico en línea: "+instruccion.linea+", la expresión no es válida.")
                    self.detenerEjecucion = True
            elif isinstance(instruccion, Si):
                valor = self.ejecutarExpresion(instruccion.expresion)
                if valor:
                    ejecutado = False
                    if isinstance(valor, (Entero, Decimal)):
                        existeAmbito = False
                        for ambitoAuxiliar in self.ambitos:
                            if str(ambitoAuxiliar.etiqueta) == str(instruccion.etiqueta):
                                if valor.valor == 1:
                                    self.ejecutar(ambitoAuxiliar)
                                    ejecutado = True
                                existeAmbito = True
                        if not existeAmbito:
                            self.mostrarError("ERROR: Semántico en línea: "+instruccion.linea +
                                              ", la etiqueta: "+instruccion.etiqueta+" no existe.")
                            self.detenerEjecucion = True
                    else:
                        self.mostrarError("ERROR: Semántico en línea: "+instruccion.linea +
                                          ", la expresión tiene que ser un entero o decimal.")
                        self.detenerEjecucion = True
                    if ejecutado:
                        break
                else:
                    self.mostrarError(
                        "ERROR: Semántico en línea: "+instruccion.linea+", expresión no válida.")
                    self.detenerEjecucion = True
            elif isinstance(instruccion, Salir):
                self.detenerEjecucion = True
            if self.detenerEjecucion:
                break

    def ejecutarAsignacion(self, instruccion):
        valorTemporal = self.ejecutarExpresion(instruccion.expresion)
        if valorTemporal:
            if isinstance(valorTemporal, Entero):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "int", valorTemporal.valor))
            elif isinstance(valorTemporal, Cadena):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "string", valorTemporal.valor))
            elif isinstance(valorTemporal, Caracter):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "char", valorTemporal.valor))
            elif isinstance(valorTemporal, Decimal):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "float", valorTemporal.valor))
            elif isinstance(valorTemporal, Arreglo):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "array", valorTemporal.valor))
            elif isinstance(valorTemporal, Registro):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "rpointer", valorTemporal))
            elif isinstance(valorTemporal, RegistroArreglo):
                self.tablaSimbolos.agregar(
                    Simbolo(instruccion.identificador, "rapointer", valorTemporal))
        else:
            self.mostrarError("ERROR: Semántico en línea: " +
                              instruccion.linea+", expresión no válida.")
            self.detenerEjecucion = True

    def ejecutarAsignacionArreglo(self, instruccion):
        simboloTemporal = self.tablaSimbolos.obtener(instruccion.identificador)
        valorArreglo = self.ejecutarExpresion(instruccion.expresion)
        if simboloTemporal:
            if valorArreglo:
                llaves = []
                for acceso in instruccion.accesos:
                    valorTemporal = self.ejecutarExpresion(acceso)
                    if not valorTemporal:
                        self.detenerEjecucion = True
                        break
                    else:
                        llaves.append(valorTemporal)
                if not self.detenerEjecucion:
                    if simboloTemporal.tipo == "array":
                        diccionarioTemporal = simboloTemporal.valor
                        diccionarios = []
                        indiceLlaves = 0
                        while indiceLlaves < len(llaves):
                            if isinstance(diccionarioTemporal, dict):
                                diccionarios.append(diccionarioTemporal)
                                if llaves[indiceLlaves].valor in diccionarioTemporal.keys():
                                    diccionarioTemporal = diccionarioTemporal[llaves[indiceLlaves].valor]
                                    indiceLlaves += 1
                                else:
                                    break
                            else:
                                break
                        if (indiceLlaves == len(llaves) - 1) and isinstance(diccionarioTemporal, Cadena):
                            if isinstance(llaves[indiceLlaves], Entero) and isinstance(valorArreglo, Caracter):
                                indice = llaves[indiceLlaves]
                                if indice.valor >= 0:
                                    listaTemporal = list(
                                        diccionarioTemporal.valor)
                                    if indice.valor >= len(listaTemporal):
                                        contadorEspacios = len(
                                            diccionarioTemporal.valor)
                                        while contadorEspacios < indice.valor:
                                            listaTemporal.append(" ")
                                            contadorEspacios += 1
                                        listaTemporal.append(
                                            valorArreglo.valor)
                                    else:
                                        listaTemporal[indice.valor] = valorArreglo.valor
                                    diccionarioTemporal = Cadena(
                                        str(''.join(listaTemporal)))
                                    indiceLlaves -= 1
                                    while indiceLlaves >= 0:
                                        diccionarioAuxiliar = diccionarioTemporal
                                        diccionarioTemporal = diccionarios[indiceLlaves]
                                        diccionarioTemporal[llaves[indiceLlaves].valor] = diccionarioAuxiliar
                                        indiceLlaves -= 1
                                    simboloTemporal.valor = diccionarioTemporal
                                    self.tablaSimbolos.actualizar(
                                        simboloTemporal)
                                else:
                                    self.detenerEjecucion = True
                                    self.mostrarError(
                                        "ERROR: Semántico en línea: "+instruccion.linea+", indice inválido.")
                            else:
                                self.detenerEjecucion = True
                                self.mostrarError(
                                    "ERROR: Semántico en línea: "+instruccion.linea+", acceso a indice inválido.")
                        elif indiceLlaves == len(llaves):
                            if isinstance(diccionarioTemporal, dict):
                                diccionarios[len(diccionarios)-1] = {}
                            if isinstance(valorArreglo, Arreglo):
                                diccionarioTemporal = valorArreglo.valor
                            else:
                                diccionarioTemporal = valorArreglo
                            indiceLlaves = len(llaves) - 1
                            while indiceLlaves >= 0:
                                diccionarioAuxiliar = diccionarioTemporal
                                diccionarioTemporal = diccionarios[indiceLlaves]
                                diccionarioTemporal[llaves[indiceLlaves].valor] = diccionarioAuxiliar
                                indiceLlaves -= 1
                            simboloTemporal.valor = diccionarioTemporal
                            self.tablaSimbolos.actualizar(simboloTemporal)
                        elif isinstance(diccionarioTemporal, dict):
                            indiceActual = indiceLlaves
                            indiceLlaves = len(llaves) - 1
                            while indiceLlaves >= 0:
                                if indiceLlaves == len(llaves) - 1:
                                    if len(llaves) != 1:
                                        diccionarioTemporal = {}
                                        if indiceLlaves == (len(diccionarios) - 1):
                                            diccionarioTemporal = diccionarios[len(
                                                diccionarios) - 1]
                                    if isinstance(valorArreglo, Arreglo):
                                        diccionarioTemporal[llaves[indiceLlaves].valor] = valorArreglo.valor
                                    else:
                                        diccionarioTemporal[llaves[indiceLlaves].valor] = valorArreglo
                                elif indiceLlaves > indiceActual:
                                    diccionarioAuxiliar = diccionarioTemporal
                                    diccionarioTemporal = {}
                                    diccionarioTemporal[llaves[indiceLlaves].valor] = diccionarioAuxiliar
                                else:
                                    diccionarioAuxiliar = diccionarioTemporal
                                    diccionarioTemporal = diccionarios[indiceLlaves]
                                    diccionarioTemporal[llaves[indiceLlaves].valor] = diccionarioAuxiliar
                                indiceLlaves -= 1
                            simboloTemporal.valor = diccionarioTemporal
                            self.tablaSimbolos.actualizar(simboloTemporal)
                        else:
                            self.detenerEjecucion = True
                            self.mostrarError(
                                "ERROR: Semántico en línea: "+instruccion.linea+", acceso a indice inválido.")
                    elif simboloTemporal.tipo == "string":
                        if len(llaves) == 1 and isinstance(llaves[0], Entero) and isinstance(valorArreglo, Caracter):
                            indice = llaves[0]
                            if indice.valor >= 0:
                                listaTemporal = list(simboloTemporal.valor)
                                if indice.valor >= len(listaTemporal):
                                    contadorEspacios = len(
                                        simboloTemporal.valor)
                                    while contadorEspacios < indice.valor:
                                        listaTemporal.append(" ")
                                        contadorEspacios += 1
                                    listaTemporal.append(valorArreglo.valor)
                                else:
                                    listaTemporal[indice.valor] = valorArreglo.valor
                                simboloTemporal.valor = str(
                                    ''.join(listaTemporal))
                                self.tablaSimbolos.actualizar(simboloTemporal)
                            else:
                                self.detenerEjecucion = True
                                self.mostrarError(
                                    "ERROR: Semántico en línea: "+instruccion.linea+", indice inválido.")
                        else:
                            self.detenerEjecucion = True
                            self.mostrarError(
                                "ERROR: Semántico en línea: "+instruccion.linea+", acceso a indice inválido.")
                    else:
                        self.detenerEjecucion = True
                        self.mostrarError(
                            "ERROR: Semántico en línea: "+instruccion.linea+", el registro no es un arreglo.")
                else:
                    self.mostrarError(
                        "ERROR: Semántico en línea: "+instruccion.linea+", valor de indices inválido.")
            else:
                self.detenerEjecucion = True
                self.mostrarError(
                    "ERROR: Semántico en línea: "+instruccion.linea+", expresión inválida.")
        else:
            self.detenerEjecucion = True
            self.mostrarError(
                "ERROR: Semántico en línea: "+instruccion.linea+", el registro no es un arreglo o string.")

    def ejecutarExpresion(self, expresion):
        if isinstance(expresion, Valor):
            if isinstance(expresion, Registro):
                return self.obtenerValorRegistro(expresion)
            if isinstance(expresion, RegistroArreglo):
                return self.obtenerValorArreglo(expresion)
            return expresion
        if isinstance(expresion, OperacionAritmetica):
            return self.ejecutarOperacionAritmetica(expresion)
        if isinstance(expresion, OperacionLogica):
            return self.ejecutarOperacionLogica(expresion)
        if isinstance(expresion, OperacionBit):
            return self.ejecutarOperacionBit(expresion)
        if isinstance(expresion, OperacionRelacional):
            return self.ejecutarOperacionRelacional(expresion)
        if isinstance(expresion, OperacionUnaria):
            return self.ejecutarOperacionUnaria(expresion)
        if isinstance(expresion, OperacionFuncion):
            return self.ejecutarOperacionFuncion(expresion)
        if isinstance(expresion, OperacionCasteo):
            return self.ejecutarOperacionCasteo(expresion)
        return None

    def ejecutarOperacionAritmetica(self, expresion):
        if isinstance(expresion.primerOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if expresion.operacion == "+":
            if isinstance(expresion.primerOperando, (Cadena, Caracter)) and isinstance(expresion.segundoOperando, (Cadena, Caracter)):
                return Cadena(str(expresion.primerOperando.valor) + str(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, Decimal) and isinstance(expresion.segundoOperando, Decimal):
                return Decimal(float(expresion.primerOperando.valor) + float(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
                return Entero(int(int(expresion.primerOperando.valor) + int(expresion.segundoOperando.valor)))
        if expresion.operacion == "-":
            if isinstance(expresion.primerOperando, Decimal) and isinstance(expresion.segundoOperando, Decimal):
                return Decimal(float(expresion.primerOperando.valor) - float(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
                return Entero(int(int(expresion.primerOperando.valor) - int(expresion.segundoOperando.valor)))
        if expresion.operacion == "*":
            if isinstance(expresion.primerOperando, Decimal) and isinstance(expresion.segundoOperando, Decimal):
                return Decimal(float(expresion.primerOperando.valor) * float(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
                return Entero(int(int(expresion.primerOperando.valor) * int(expresion.segundoOperando.valor)))
        if expresion.operacion == "/":
            if isinstance(expresion.primerOperando, Decimal) and isinstance(expresion.segundoOperando, Decimal):
                if expresion.segundoOperando.valor == 0:
                    return None
                return Decimal(float(expresion.primerOperando.valor) / float(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
                if expresion.segundoOperando.valor == 0:
                    return None
                return Entero(int(int(expresion.primerOperando.valor) / int(expresion.segundoOperando.valor)))
        if expresion.operacion == "%":
            if isinstance(expresion.primerOperando, Decimal) and isinstance(expresion.segundoOperando, Decimal):
                if expresion.segundoOperando.valor == 0:
                    return None
                return Decimal(float(expresion.primerOperando.valor) % float(expresion.segundoOperando.valor))
            if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
                if expresion.segundoOperando.valor == 0:
                    return None
                return Entero(int(int(expresion.primerOperando.valor) % int(expresion.segundoOperando.valor)))
        return None

    def ejecutarOperacionLogica(self, expresion):
        if isinstance(expresion.primerOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, Entero) and isinstance(expresion.segundoOperando, Entero):
            if (expresion.primerOperando.valor == 0 or expresion.primerOperando.valor == 1) and (expresion.segundoOperando.valor == 0 or expresion.segundoOperando.valor == 1):
                if expresion.operacion == "&&":
                    if expresion.primerOperando.valor == 0 and expresion.segundoOperando.valor == 0:
                        return Entero(int(0))
                    if expresion.primerOperando.valor == 0 and expresion.segundoOperando.valor == 1:
                        return Entero(int(0))
                    if expresion.primerOperando.valor == 1 and expresion.segundoOperando.valor == 0:
                        return Entero(int(0))
                    if expresion.primerOperando.valor == 1 and expresion.segundoOperando.valor == 1:
                        return Entero(int(1))
                if expresion.operacion == "||":
                    if expresion.primerOperando.valor == 0 and expresion.segundoOperando.valor == 0:
                        return Entero(int(0))
                    if expresion.primerOperando.valor == 0 and expresion.segundoOperando.valor == 1:
                        return Entero(int(1))
                    if expresion.primerOperando.valor == 1 and expresion.segundoOperando.valor == 0:
                        return Entero(int(1))
                    if expresion.primerOperando.valor == 1 and expresion.segundoOperando.valor == 1:
                        return Entero(int(1))
                if expresion.operacion == "xor":
                    if expresion.primerOperando.valor != expresion.segundoOperando.valor:
                        return Entero(int(1))
                    else:
                        return Entero(int(0))
        return None

    def ejecutarOperacionBit(self, expresion):
        if isinstance(expresion.primerOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
            if expresion.operacion == "&":
                return Entero(int(expresion.primerOperando.valor) & int(expresion.segundoOperando.valor))
            if expresion.operacion == "|":
                return Entero(int(expresion.primerOperando.valor) | int(expresion.segundoOperando.valor))
            if expresion.operacion == "^":
                return Entero(int(expresion.primerOperando.valor) ^ int(expresion.segundoOperando.valor))
            if expresion.operacion == "<<":
                return Entero(int(expresion.primerOperando.valor) << int(expresion.segundoOperando.valor))
            if expresion.operacion == ">>":
                return Entero(int(expresion.primerOperando.valor) >> int(expresion.segundoOperando.valor))
        return None

    def ejecutarOperacionRelacional(self, expresion):
        if isinstance(expresion.primerOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.primerOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.primerOperando)
            if valor:
                expresion.primerOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, Registro):
            valor = self.obtenerValorRegistro(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if isinstance(expresion.segundoOperando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.segundoOperando)
            if valor:
                expresion.segundoOperando = valor
            else:
                return None
        if expresion.operacion == "==":
            if expresion.primerOperando.valor == expresion.segundoOperando.valor:
                return Entero(int(1))
            else:
                return Entero(int(0))
        if expresion.operacion == "!=":
            if expresion.primerOperando.valor != expresion.segundoOperando.valor:
                return Entero(int(1))
            else:
                return Entero(int(0))
        if isinstance(expresion.primerOperando, (Entero, Decimal)) and isinstance(expresion.segundoOperando, (Entero, Decimal)):
            if expresion.operacion == ">=":
                if expresion.primerOperando.valor >= expresion.segundoOperando.valor:
                    return Entero(int(1))
                else:
                    return Entero(int(0))
            if expresion.operacion == "<=":
                if expresion.primerOperando.valor <= expresion.segundoOperando.valor:
                    return Entero(int(1))
                else:
                    return Entero(int(0))
            if expresion.operacion == ">":
                if expresion.primerOperando.valor > expresion.segundoOperando.valor:
                    return Entero(int(1))
                else:
                    return Entero(int(0))
            if expresion.operacion == "<":
                if expresion.primerOperando.valor < expresion.segundoOperando.valor:
                    return Entero(int(1))
                else:
                    return Entero(int(0))
        return None

    def ejecutarOperacionUnaria(self, expresion):
        if expresion.operacion == "&":
            if isinstance(expresion.operando, Registro):
                valor = self.obtenerValorRegistro(expresion.operando)
                if valor:
                    return expresion.operando
                else:
                    return None
            if isinstance(expresion.operando, RegistroArreglo):
                valor = self.obtenerValorArreglo(expresion.operando)
                if valor:
                    return expresion.operando
                else:
                    return None
        else:
            if isinstance(expresion.operando, Registro):
                valor = self.obtenerValorRegistro(expresion.operando)
                if valor:
                    expresion.operando = valor
                else:
                    return None
            if isinstance(expresion.operando, RegistroArreglo):
                valor = self.obtenerValorArreglo(expresion.operando)
                if valor:
                    expresion.operando = valor
                else:
                    return None
            if expresion.operacion == "-":
                if isinstance(expresion.operando, Entero):
                    return Entero(int(expresion.operando.valor) * -1)
                if isinstance(expresion.operando, Decimal):
                    return Decimal(float(expresion.operando.valor) * -1)
            if expresion.operacion == "!":
                if isinstance(expresion.operando, (Entero, Decimal)):
                    if int(expresion.operando.valor) == 1:
                        return Entero(0)
                    if int(expresion.operando.valor) == 0:
                        return Entero(1)
            if expresion.operacion == "~":
                if isinstance(expresion.operando, (Entero, Decimal)):
                    return Entero(~int(expresion.operando.valor))
        return None

    def ejecutarOperacionFuncion(self, expresion):
        if expresion.funcion == "read":
            textoInicial = self.consola.toPlainText()
            leerEntrada = True
            self.consola.setReadOnly(False)
            self.consola.setFocus()
            cursorTemporal = self.consola.textCursor()
            cursorTemporal.setPosition(len(textoInicial))
            self.consola.setTextCursor(cursorTemporal)
            while leerEntrada:
                QtGui.QGuiApplication.processEvents()
                textoTemporal = self.consola.toPlainText()
                time.sleep(0.025)
                if len(textoTemporal) < len(textoInicial):
                    self.consola.setPlainText(textoInicial)
                    cursorTemporal = self.consola.textCursor()
                    cursorTemporal.setPosition(len(textoInicial))
                    self.consola.setTextCursor(cursorTemporal)
                elif len(textoTemporal) > len(textoInicial):
                    if textoInicial == textoTemporal[0:len(textoInicial)]:
                        if textoTemporal[len(textoTemporal) - 1] == "\n":
                            entrada = textoTemporal[len(
                                textoInicial):len(textoTemporal)-1]
                            leerEntrada = False
                            self.consola.setReadOnly(True)
                            cursorTemporal = self.consola.textCursor()
                            cursorTemporal.setPosition(len(textoTemporal))
                            self.consola.setTextCursor(cursorTemporal)
                            if entrada != "\n":
                                verificando = re.fullmatch(r'\d+', entrada)
                                if verificando:
                                    return Entero(int(entrada))
                                else:
                                    verificando = re.fullmatch(
                                        r'\d+\.\d+', entrada)
                                    if verificando:
                                        return Decimal(float(entrada))
                                    else:
                                        if len(entrada) == 1:
                                            return Caracter(str(entrada))
                                        else:
                                            return Cadena(str(entrada))
                    else:
                        self.consola.setPlainText(textoInicial)
                        cursorTemporal = self.consola.textCursor()
                        cursorTemporal.setPosition(len(textoInicial))
                        self.consola.setTextCursor(cursorTemporal)
        if expresion.funcion == "abs":
            if isinstance(expresion.operando, Registro):
                valor = self.obtenerValorRegistro(expresion.operando)
                if valor:
                    expresion.operando = valor
                else:
                    return None
            if isinstance(expresion.operando, RegistroArreglo):
                valor = self.obtenerValorArreglo(expresion.operando)
                if valor:
                    expresion.operando = valor
                else:
                    return None
            if isinstance(expresion.operando, (Entero, Decimal)):
                if expresion.operando.valor < 0:
                    expresion.operando.valor *= -1
                if isinstance(expresion.operando, Entero):
                    return Entero(int(expresion.operando.valor))
                if isinstance(expresion.operando, Decimal):
                    return Decimal(float(expresion.operando.valor))
        if expresion.funcion == "array":
            return Arreglo({})
        return None

    def ejecutarOperacionCasteo(self, expresion):
        if isinstance(expresion.operando, Registro):
            valor = self.obtenerValorRegistro(expresion.operando)
            if valor:
                expresion.operando = valor
            else:
                return None
        if isinstance(expresion.operando, RegistroArreglo):
            valor = self.obtenerValorArreglo(expresion.operando)
            if valor:
                expresion.operando = valor
            else:
                return None
        if isinstance(expresion.operando, Arreglo):
            diccionarioTemporal = expresion.operando.valor
            while isinstance(diccionarioTemporal, dict):
                llaves = []
                for llave in diccionarioTemporal.keys():
                    llaves.append(llave)
                if len(llaves) > 0:
                    diccionarioTemporal = diccionarioTemporal[llaves[0]]
                else:
                    diccionarioTemporal = None
            expresion.operando = diccionarioTemporal
        if expresion.tipo == "int":
            if isinstance(expresion.operando, (Entero, Decimal)):
                return Entero(int(expresion.operando.valor))
            if isinstance(expresion.operando, Caracter):
                return Entero(int(ord(expresion.operando.valor)))
            if isinstance(expresion.operando, Cadena):
                if len(expresion.operando.valor) > 0:
                    return Entero(int(ord(expresion.operando.valor[0])))
                else:
                    return Entero(0)
        if expresion.tipo == "char":
            if isinstance(expresion.operando, (Entero, Decimal)):
                valor = expresion.operando.valor
                if valor >= 0 and valor <= 255:
                    return Caracter(chr(int(valor)))
                if valor >= 255:
                    return Caracter(chr(int(valor) % 256))
            if isinstance(expresion.operando, Caracter):
                return Caracter(expresion.operando.valor)
            if isinstance(expresion.operando, Cadena):
                if len(expresion.operando.valor) > 0:
                    return Caracter(expresion.operando.valor[0])
                else:
                    return Caracter('')
        if expresion.tipo == "float":
            if isinstance(expresion.operando, (Entero, Decimal)):
                return Decimal(float(expresion.operando.valor))
            if isinstance(expresion.operando, Caracter):
                return Decimal(float(ord(expresion.operando.valor)))
            if isinstance(expresion.operando, Cadena):
                if len(expresion.operando.valor) > 0:
                    return Decimal(float(ord(expresion.operando.valor[0])))
                else:
                    return Decimal(0.0)
        return None

    def obtenerValorRegistro(self, registro):
        simbolo = self.tablaSimbolos.obtener(registro.registro)
        if simbolo:
            if simbolo.tipo == "rpointer":
                return self.obtenerValorRegistro(simbolo.valor)
            if simbolo.tipo == "rapointer":
                return self.obtenerValorArreglo(simbolo.valor)
            valor = self.transformarSimbolo(simbolo)
            if valor:
                return valor
        return None

    def obtenerValorArreglo(self, registroArreglo):
        simbolo = self.tablaSimbolos.obtener(registroArreglo.registro)
        if simbolo:
            if simbolo.tipo == "array":
                llaves = []
                for acceso in registroArreglo.accesos:
                    valorTemporal = self.ejecutarExpresion(acceso)
                    if not valorTemporal:
                        return None
                    llaves.append(valorTemporal.valor)
                diccionarioTemporal = simbolo.valor
                indiceLlaves = 0
                valorEncontrado = False
                valorFinal = None
                while indiceLlaves < len(llaves):
                    if isinstance(diccionarioTemporal, dict):
                        if llaves[indiceLlaves] in diccionarioTemporal:
                            if indiceLlaves == len(llaves) - 1:
                                valorEncontrado = True
                                valorFinal = diccionarioTemporal[llaves[indiceLlaves]]
                            else:
                                diccionarioTemporal = diccionarioTemporal[llaves[indiceLlaves]]
                    indiceLlaves += 1
                if valorEncontrado:
                    return valorFinal
            if simbolo.tipo == "string":
                llaves = []
                for acceso in registroArreglo.accesos:
                    valorTemporal = self.ejecutarExpresion(acceso)
                    if not valorTemporal:
                        return None
                    llaves.append(valorTemporal)
                if len(llaves) == 1:
                    if isinstance(llaves[0], (Entero, Decimal)):
                        if int(llaves[0].valor) < len(simbolo.valor) and int(llaves[0].valor) >= 0:
                            return Caracter(simbolo.valor[llaves[0].valor])
        return None

    def transformarSimbolo(self, simbolo):
        if simbolo.tipo == "int":
            return Entero(simbolo.valor)
        elif simbolo.tipo == "char":
            return Caracter(simbolo.valor)
        elif simbolo.tipo == "string":
            return Cadena(simbolo.valor)
        elif simbolo.tipo == "float":
            return Decimal(simbolo.valor)
        elif simbolo.tipo == "array":
            return Arreglo(simbolo.valor)
        return None

    def mostrarError(self, mensaje):
        self.consola.appendPlainText(mensaje)
        cursorTemporal = self.consola.textCursor()
        cursorTemporal.setPosition(len(self.consola.toPlainText()))
        self.consola.setTextCursor(cursorTemporal)

    def graficarAST(self, ast):
        dot = Digraph('G', filename='ast', format='png')
        self.identificadorNodo = 0
        dot.attr("node", shape="box")
        dot.node(str(self.identificadorNodo), "INSTRUCCIONES")
        nodoPadre = self.identificadorNodo
        for instruccion in ast:
            if isinstance(instruccion, Principal):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "PRINCIPAL")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreInstruccion = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "main")
                dot.edge(str(nodoPadreInstruccion),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), ":")
                dot.edge(str(nodoPadreInstruccion),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Etiqueta):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "ETIQUETA")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreEtiqueta = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         str(instruccion.etiqueta))
                dot.edge(str(nodoPadreEtiqueta),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), ":")
                dot.edge(str(nodoPadreEtiqueta),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Salto):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "SALTO")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreSalto = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "goto")
                dot.edge(str(nodoPadreSalto),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         str(instruccion.etiqueta))
                dot.edge(str(nodoPadreSalto),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), ";")
                dot.edge(str(nodoPadreSalto),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Asignacion):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "ASIGNACION")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreAsignacion = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         instruccion.identificador)
                dot.edge(str(nodoPadreAsignacion),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "=")
                dot.edge(str(nodoPadreAsignacion),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "EXPRESION")
                dot.edge(str(nodoPadreAsignacion),
                         str(self.identificadorNodo))
                self.graficarExpresion(
                    dot, instruccion.expresion, self.identificadorNodo)
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), ";")
                dot.edge(str(nodoPadreAsignacion),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, AsignacionArreglo):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "ASIGNACION ARREGLO")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreAsignacionArreglo = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         instruccion.identificador)
                dot.edge(str(nodoPadreAsignacionArreglo),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "ACCESOS")
                dot.edge(str(nodoPadreAsignacionArreglo),
                         str(self.identificadorNodo))
                self.graficarAccesos(
                    dot, instruccion.accesos, self.identificadorNodo)
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "=")
                dot.edge(str(nodoPadreAsignacionArreglo),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "EXPRESION")
                dot.edge(str(nodoPadreAsignacionArreglo),
                         str(self.identificadorNodo))
                self.graficarExpresion(
                    dot, instruccion.expresion, self.identificadorNodo)
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ";")
                dot.edge(str(nodoPadreAsignacionArreglo),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Eliminar):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "ELIMINAR")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreEliminar = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "unset")
                dot.edge(str(nodoPadreEliminar),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "(")
                dot.edge(str(nodoPadreEliminar),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         instruccion.registro)
                dot.edge(str(nodoPadreEliminar),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ")")
                dot.edge(str(nodoPadreEliminar),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ";")
                dot.edge(str(nodoPadreEliminar),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Imprimir):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "IMPRIMIR")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreImprimir = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "print")
                dot.edge(str(nodoPadreImprimir),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "(")
                dot.edge(str(nodoPadreImprimir),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "EXPRESION")
                dot.edge(str(nodoPadreImprimir),
                         str(self.identificadorNodo))
                self.graficarExpresion(
                    dot, instruccion.expresion, self.identificadorNodo)
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ")")
                dot.edge(str(nodoPadreImprimir),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ";")
                dot.edge(str(nodoPadreImprimir),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Si):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "SI")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreSi = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "if")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "(")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "EXPRESION")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.graficarExpresion(
                    dot, instruccion.expresion, self.identificadorNodo)
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ")")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         "goto")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         instruccion.etiqueta)
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         ";")
                dot.edge(str(nodoPadreSi),
                         str(self.identificadorNodo))
            elif isinstance(instruccion, Salir):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "SALIR")
                dot.edge(str(nodoPadre),
                         str(self.identificadorNodo))
                nodoPadreInstruccion = self.identificadorNodo
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), "exit")
                dot.edge(str(nodoPadreInstruccion),
                         str(self.identificadorNodo))
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo), ";")
                dot.edge(str(nodoPadreInstruccion),
                         str(self.identificadorNodo))
        dot.view()

    def graficarExpresionBinaria(self, dot, operando, primerOperando, segundoOperando):
        nodoPadre = self.identificadorNodo
        self.identificadorNodo += 1
        dot.node(str(self.identificadorNodo),
                 str("VALOR"))
        dot.edge(str(nodoPadre),
                 str(self.identificadorNodo))
        self.graficarValor(dot, primerOperando, self.identificadorNodo)
        self.identificadorNodo += 1
        dot.node(str(self.identificadorNodo),
                 str(operando))
        dot.edge(str(nodoPadre),
                 str(self.identificadorNodo))
        self.identificadorNodo += 1
        dot.node(str(self.identificadorNodo),
                 str("VALOR"))
        dot.edge(str(nodoPadre),
                 str(self.identificadorNodo))
        self.graficarValor(dot, segundoOperando, self.identificadorNodo)

    def graficarExpresion(self, dot, expresion, nodoPadreExpresion):
        if isinstance(expresion, OperacionAritmetica):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "ARITMETICA")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            self.graficarExpresionBinaria(
                dot, expresion.operacion, expresion.primerOperando, expresion.segundoOperando)
        elif isinstance(expresion, OperacionLogica):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "LOGICA")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            self.graficarExpresionBinaria(
                dot, expresion.operacion, expresion.primerOperando, expresion.segundoOperando)
        elif isinstance(expresion, OperacionBit):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "BIT")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            self.graficarExpresionBinaria(
                dot, expresion.operacion, expresion.primerOperando, expresion.segundoOperando)
        elif isinstance(expresion, OperacionRelacional):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "RELACIONAL")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            self.graficarExpresionBinaria(
                dot, expresion.operacion, expresion.primerOperando, expresion.segundoOperando)
        elif isinstance(expresion, OperacionUnaria):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "UNARIA")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            nodoPadreUnaria = self.identificadorNodo
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(expresion.operacion))
            dot.edge(str(nodoPadreUnaria),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("VALOR"))
            dot.edge(str(nodoPadreUnaria),
                     str(self.identificadorNodo))
            self.graficarValor(dot, expresion.operando, self.identificadorNodo)
        elif isinstance(expresion, OperacionFuncion):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "FUNCION")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            nodoPadreFuncion = self.identificadorNodo
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(expresion.funcion))
            dot.edge(str(nodoPadreFuncion),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("("))
            dot.edge(str(nodoPadreFuncion),
                     str(self.identificadorNodo))
            if(str(expresion.operando) != ")"):
                self.identificadorNodo += 1
                dot.node(str(self.identificadorNodo),
                         str("VALOR"))
                dot.edge(str(nodoPadreFuncion),
                         str(self.identificadorNodo))
                self.graficarValor(dot, expresion.operando,
                                   self.identificadorNodo)
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(")"))
            dot.edge(str(nodoPadreFuncion),
                     str(self.identificadorNodo))
        elif isinstance(expresion, OperacionCasteo):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "CASTEO")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            nodoPadreCasteo = self.identificadorNodo
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("("))
            dot.edge(str(nodoPadreCasteo),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(expresion.tipo))
            dot.edge(str(nodoPadreCasteo),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(")"))
            dot.edge(str(nodoPadreCasteo),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("VALOR"))
            dot.edge(str(nodoPadreCasteo),
                     str(self.identificadorNodo))
            self.graficarValor(dot, expresion.operando,
                               str(self.identificadorNodo))
        elif isinstance(expresion, Valor):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "VALOR")
            dot.edge(str(nodoPadreExpresion),
                     str(self.identificadorNodo))
            nodoPadreValor = self.identificadorNodo
            self.graficarValor(dot, expresion, nodoPadreValor)

    def graficarValorAtomico(self, dot, tipo, valor, nodoPadreValor):
        self.identificadorNodo += 1
        dot.node(str(self.identificadorNodo), tipo)
        dot.edge(str(nodoPadreValor),
                 str(self.identificadorNodo))
        nodoPadre = self.identificadorNodo
        self.identificadorNodo += 1
        dot.node(str(self.identificadorNodo),
                 str(valor))
        dot.edge(str(nodoPadre),
                 str(self.identificadorNodo))

    def graficarValor(self, dot, valor, nodoPadreValor):
        if isinstance(valor, Entero):
            self.graficarValorAtomico(
                dot, "ENTERO", valor.valor, nodoPadreValor)
        elif isinstance(valor, Caracter):
            self.graficarValorAtomico(
                dot, "CARACTER", "'"+str(valor.valor)+"'", nodoPadreValor)
        elif isinstance(valor, Cadena):
            self.graficarValorAtomico(
                dot, "CADENA", "\""+str(valor.valor)+"\"", nodoPadreValor)
        elif isinstance(valor, Decimal):
            self.graficarValorAtomico(
                dot, "DECIMAL", valor.valor, nodoPadreValor)
        elif isinstance(valor, Registro):
            self.graficarValorAtomico(
                dot, "REGISTRO", valor.registro, nodoPadreValor)
        elif isinstance(valor, RegistroArreglo):
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo), "ARREGLO")
            dot.edge(str(nodoPadreValor),
                     str(self.identificadorNodo))
            nodoPadre = self.identificadorNodo
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str(valor.registro))
            dot.edge(str(nodoPadre),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("ACCESOS"))
            dot.edge(str(nodoPadre),
                     str(self.identificadorNodo))
            self.graficarAccesos(dot, valor.accesos, self.identificadorNodo)

    def graficarAccesos(self, dot, accesos, nodoPadreAccesos):
        for acceso in accesos:
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("["))
            dot.edge(str(nodoPadreAccesos),
                     str(self.identificadorNodo))
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("EXPRESION"))
            dot.edge(str(nodoPadreAccesos),
                     str(self.identificadorNodo))
            self.graficarExpresion(dot, acceso, self.identificadorNodo)
            self.identificadorNodo += 1
            dot.node(str(self.identificadorNodo),
                     str("]"))
            dot.edge(str(nodoPadreAccesos),
                     str(self.identificadorNodo))
