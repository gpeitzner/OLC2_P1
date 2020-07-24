import ply.yacc as yacc
import ply.lex as lex
from valores import *
from expresiones import *
from instrucciones import *
from PyQt5 import QtWidgets, QtGui
from terror import TError

palabrasReservadas = {
    'main': 'main',
    'goto': 'goto',
    'unset': 'unset',
    'print': 'print',
    'if': 'if',
    'exit': 'exit',
    'read': 'read',
    'int': 'int',
    'float': 'float',
    'char': 'char',
    'abs': 'abs',
    'array': 'array',
    'xor': 'xor'
}

tokens = [
    'dosPuntos',
    'puntoComa',
    'igual',
    'parentesisAbre',
    'parentesisCierra',
    'corcheteAbre',
    'corcheteCierra',
    'mas',
    'menos',
    'asterisco',
    'division',
    'residuo',
    'andLogico',
    'orLogico',
    'andBit',
    'orBit',
    'xorBit',
    'desplazamientoIzquierda',
    'desplazamientoDerecha',
    'equivale',
    'diferente',
    'mayorIgual',
    'menorIgual',
    'mayor',
    'menor',
    'negacionLogica',
    'negacionBit',
    'entero',
    'cadena',
    'caracter',
    'decimal',
    'identificador',
    'registro'
] + list(palabrasReservadas.values())

t_dosPuntos = r':'
t_puntoComa = r';'
t_igual = r'='
t_parentesisAbre = r'\('
t_parentesisCierra = r'\)'
t_corcheteAbre = r'\['
t_corcheteCierra = r'\]'
t_mas = r'\+'
t_menos = r'-'
t_asterisco = r'\*'
t_division = r'/'
t_residuo = r'%'
t_andLogico = r'&&'
t_orLogico = r'\|\|'
t_andBit = r'&'
t_orBit = r'\|'
t_xorBit = r'\^'
t_desplazamientoIzquierda = r'<<'
t_desplazamientoDerecha = r'>>'
t_equivale = r'=='
t_diferente = r'!='
t_mayorIgual = r'>='
t_menorIgual = r'<='
t_mayor = r'>'
t_menor = r'<'
t_negacionLogica = r'!'
t_negacionBit = r'~'


def t_decimal(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Valor del float muy grande %d", t.value)
        t.value = 0
    return t


def t_entero(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Valor del entero muy grande %d", t.value)
        t.value = 0
    return t


def t_registro(t):
    r'(\$t)\d+|(\$a)\d+|(\$v)\d+|(\$ra)|(\$s)\d+|(\$sp)'
    return t


def t_identificador(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = palabrasReservadas.get(t.value.lower(), 'identificador')
    return t


def t_caracter(t):
    r'\'.{1}\'|\".{1}\"'
    t.value = t.value[1:-1]
    return t


def t_cadena(t):
    r'\'[^\']*\'|\"[^\"]*\"'
    t.value = t.value[1:-1]
    return t


def t_comentario(t):
    r'\#.*\n'
    t.lexer.lineno += 1


t_ignore = " \t"


def t_nuevaLinea(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    mostrarError("ERROR: Léxico en: "+str(t.value[0])+", línea: " +
                 str(t.lineno)+", columna: "+str(find_column(input_, t))+".")
    erroresLexicos_.append(TError(str(t.value[0]), str(
        t.lineno), str(find_column(input_, t))))
    t.lexer.skip(1)


lexer = lex.lex()

gramatical = ""


def p_init(t):
    'init   :   main dosPuntos cuerpo'
    t[1] = [Principal()]
    if(t[3] != None):
        t[0] = t[1] + t[3]
    else:
        t[0] = t[1]
    global gramatical
    gramaticalTemporal = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Gramatical</title></head><body>'
    gramaticalTemporal += '<center><h1>Gramatical</h1>'
    gramaticalTemporal += '<table border="1"><tr><th>Produccion</th><th>Regla</th></th>'
    gramatical += '<tr>'
    gramatical += '<td>INIT -> main: CUERPO</td>'
    gramatical += '<td>INIT.val = Principal() + CUERPO.val</td>'
    gramatical += '</tr>'
    gramaticalTemporal += gramatical
    gramaticalTemporal += '</table><center>'
    gramaticalTemporal += '</body></html>'
    f = open("gramatical.html", "w")
    f.write(gramaticalTemporal)
    f.close()


def p_cuerpo(t):
    'cuerpo :   instrucciones'
    t[0] = t[1]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>CUERPO -> INSTRUCCIONES</td>'
    gramatical += '<td>CUERPO.val = INSTRUCCIONES.val</td>'
    gramatical += '</tr>'


def p_cuerpo_vacio(t):
    'cuerpo :   '
    t[0] = None
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>CUERPO -> </td>'
    gramatical += '<td>CUERPO.val = None</td>'
    gramatical += '</tr>'


def p_instrucciones_lista(t):
    'instrucciones  :   instrucciones instruccion'
    t[1].append(t[2])
    t[0] = t[1]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>INSTRUCCIONES -> INSTRUCCIONES INSTRUCCION</td>'
    gramatical += '<td>INSTRUCCIONES1.add(INSTRUCCION); INSTRUCCIONES.val = INSTRUCCIONES1</td>'
    gramatical += '</tr>'


def p_instrucciones_instruccion(t):
    'instrucciones  :   instruccion'
    t[0] = [t[1]]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>INSTRUCCIONES -> INSTRUCCION</td>'
    gramatical += '<td>INSTRUCCIONES.val = new list(INSTRUCCION)</td>'
    gramatical += '</tr>'


def p_instruccion(t):
    '''instruccion  :   etiqueta
                    |   salto
                    |   asignacion
                    |   asignacion_arreglo
                    |   eliminar
                    |   imprimir
                    |   si
                    |   salir
    '''
    t[0] = t[1]
    global gramatical
    gramatical += '<tr>'
    if isinstance(t[1], Etiqueta):
        gramatical += '<td>INSTRUCCION -> ETIQUETA </td>'
        gramatical += '<td>INSTRUCCION.val =  ETIQUETA.val</td>'
    elif isinstance(t[1], Salto):
        gramatical += '<td>INSTRUCCION -> SALTO </td>'
        gramatical += '<td>INSTRUCCION.val =  SALTO.val</td>'
    elif isinstance(t[1], Asignacion):
        gramatical += '<td>INSTRUCCION -> ASIGNACION </td>'
        gramatical += '<td>INSTRUCCION.val =  ASIGNACION.val</td>'
    elif isinstance(t[1], AsignacionArreglo):
        gramatical += '<td>INSTRUCCION -> ASIGNACION_ARREGLO </td>'
        gramatical += '<td>INSTRUCCION.val =  ASIGNACION_ARREGLO.val</td>'
    elif isinstance(t[1], Eliminar):
        gramatical += '<td>INSTRUCCION -> ELIMINAR </td>'
        gramatical += '<td>INSTRUCCION.val =  Eliminar.val</td>'
    elif isinstance(t[1], Imprimir):
        gramatical += '<td>INSTRUCCION -> IMPRIMIR </td>'
        gramatical += '<td>INSTRUCCION.val =  Imprimir.val</td>'
    elif isinstance(t[1], Si):
        gramatical += '<td>INSTRUCCION -> SI </td>'
        gramatical += '<td>INSTRUCCION.val =  SI.val</td>'
    elif isinstance(t[1], Salir):
        gramatical += '<td>INSTRUCCION -> SALIR </td>'
        gramatical += '<td>INSTRUCCION.val =  SALIR.val</td>'
    gramatical += '</tr>'


def p_etiqueta(t):
    'etiqueta   :   identificador dosPuntos'
    t[0] = Etiqueta(t[1], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ETIQUETA -> '+str(t[1])+':</td>'
    gramatical += '<td>ETIQUETA.val = Etiqueta('+str(t[1])+', t.lineno)</td>'
    gramatical += '</tr>'


def p_salto(t):
    'salto  :   goto identificador puntoComa'
    t[0] = Salto(t[2], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>SALTO -> goto '+str(t[1])+';</td>'
    gramatical += '<td>SALTO.val = Salto('+str(t[1])+', t.lineno)</td>'
    gramatical += '</tr>'


def p_asignacion(t):
    'asignacion :   registro igual expresion puntoComa'
    t[0] = Asignacion(t[1], t[3], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ASIGNACION -> '+str(t[1])+' = EXPRESION;</td>'
    gramatical += '<td>ASIGNACION.val = Asignacion('+str(
        t[1])+', EXPRESION.val, t.lineno)</td>'
    gramatical += '</tr>'


def p_asignacion_arreglo(t):
    'asignacion_arreglo :   registro accesos igual expresion puntoComa'
    t[0] = AsignacionArreglo(t[1], t[2], t[4], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ASIGNACION_ARREGLO -> ' + \
        str(t[1])+' ACCESOS = EXPRESION;</td>'
    gramatical += '<td>ASIGNACION_ARREGLO.val = AsignacionArreglo('+str(
        t[1])+', ACCESOS.val, EXPRESION.val, t.lineno)</td>'
    gramatical += '</tr>'


def p_eliminar(t):
    'eliminar   :   unset parentesisAbre registro parentesisCierra puntoComa'
    t[0] = Eliminar(t[3], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ELIMINAR -> unset( EXPRESION );</td>'
    gramatical += '<td>ELIMINAR.val = Eliminar(EXPRESION.val, t.lineno)</td>'
    gramatical += '</tr>'


def p_imprimir(t):
    'imprimir   :   print parentesisAbre expresion parentesisCierra puntoComa'
    t[0] = Imprimir(t[3], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>IMPRIMIR -> print( EXPRESION );</td>'
    gramatical += '<td>IMPRIMIR.val = Imprimir(EXPRESION.val, t.lineno)</td>'
    gramatical += '</tr>'


def p_si(t):
    'si :   if parentesisAbre expresion parentesisCierra goto identificador puntoComa'
    t[0] = Si(t[3], t[6], str(t.slice[1].lineno))
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>SI -> if ( EXPRESION ) goto '+str(t[6])+';</td>'
    gramatical += '<td>SI.val = Si(EXPRESION.val, ' + \
        str(t[6])+', t.lineno)</td>'
    gramatical += '</tr>'


def p_salir(t):
    'salir  :   exit puntoComa'
    t[0] = Salir()
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>SALIR -> exit ;</td>'
    gramatical += '<td>SALIR.val = Salir()</td>'
    gramatical += '</tr>'


def p_expression_aritmetica(t):
    '''expresion    :   valor mas valor
                    |   valor menos valor
                    |   valor asterisco valor
                    |   valor division valor
                    |   valor residuo valor
    '''
    t[0] = OperacionAritmetica(t[1], t[2], t[3])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION ->  VALOR '+str(t[2])+' VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionAritmetica(VALOR.val,' + \
        t[2]+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_logica(t):
    '''expresion    :   valor andLogico valor
                    |   valor orLogico valor
                    |   valor xor valor
    '''
    t[0] = OperacionLogica(t[1], t[2], t[3])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION ->  VALOR '+str(t[2])+' VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionLogica(VALOR.val,'+str(
        t[2])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_bit(t):
    '''expresion    :   valor andBit valor
                    |   valor orBit valor
                    |   valor xorBit valor
                    |   valor desplazamientoIzquierda valor
                    |   valor desplazamientoDerecha valor
    '''
    t[0] = OperacionBit(t[1], t[2], t[3])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION ->  VALOR '+str(t[2])+' VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionBit(VALOR.val,'+str(
        t[2])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_relacional(t):
    '''expresion    :   valor equivale valor
                    |   valor diferente valor
                    |   valor mayorIgual valor
                    |   valor menorIgual valor
                    |   valor mayor valor
                    |   valor menor valor
    '''
    t[0] = OperacionRelacional(t[1], t[2], t[3])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION ->  VALOR '+str(t[2])+' VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionRelacional(VALOR.val,'+str(
        t[2])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_unaria(t):
    '''expresion    :   menos valor
                    |   andBit valor
                    |   negacionLogica valor
                    |   negacionBit valor
    '''
    t[0] = OperacionUnaria(t[1], t[2])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION -> '+str(t[1])+' VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionCasteo('+str(
        t[1])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_funcion(t):
    '''expresion    :   read parentesisAbre parentesisCierra
                    |   abs parentesisAbre valor parentesisCierra
                    |   array parentesisAbre parentesisCierra
    '''
    t[0] = OperacionFuncion(t[1], t[3])
    global gramatical
    gramatical += '<tr>'
    if str(t[1]) == "abs":
        gramatical += '<td>EXPRESION -> '+str(t[1])+'( VALOR )</td>'
    else:
        gramatical += '<td>EXPRESION -> '+str(t[1])+'()</td>'
    gramatical += '<td>EXPRESION.val = OperacionFuncion('+str(
        t[1])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_casteo(t):
    '''expresion    :   parentesisAbre int parentesisCierra valor
                    |   parentesisAbre float parentesisCierra valor
                    |   parentesisAbre char parentesisCierra valor
    '''
    t[0] = OperacionCasteo(t[2], t[4])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION -> ('+str(t[2])+') VALOR</td>'
    gramatical += '<td>EXPRESION.val = OperacionCasteo('+str(
        t[2])+', VALOR.val)</td>'
    gramatical += '</tr>'


def p_expresion_valor(t):
    'expresion    :   valor'
    t[0] = t[1]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>EXPRESION -> VALOR</td>'
    gramatical += '<td>EXPRESION.val = VALOR.val</td>'
    gramatical += '</tr>'


def p_valor_entero(t):
    'valor  :   entero'
    t[0] = Entero(t[1])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+'</td>'
    gramatical += '<td>VALOR.val = Entero('+str(t[1])+')</td>'
    gramatical += '</tr>'


def p_valor_cadena(t):
    'valor  :   cadena'
    t[0] = Cadena(t[1])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+'</td>'
    gramatical += '<td>VALOR.val = Cadena('+str(t[1])+')</td>'
    gramatical += '</tr>'


def p_valor_caracter(t):
    'valor  :   caracter'
    t[0] = Caracter(t[1])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+'</td>'
    gramatical += '<td>VALOR.val = Caracter('+str(t[1])+')</td>'
    gramatical += '</tr>'


def p_valor_decimal(t):
    'valor  :   decimal'
    t[0] = Decimal(t[1])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+'</td>'
    gramatical += '<td>VALOR.val = Decimal('+str(t[1])+')</td>'
    gramatical += '</tr>'


def p_valor_registro(t):
    'valor  :   registro'
    t[0] = Registro(t[1])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+'</td>'
    gramatical += '<td>VALOR.val = Registro('+str(t[1])+')</td>'
    gramatical += '</tr>'


def p_valor_registro_arreglo(t):
    'valor  :   registro accesos'
    t[0] = RegistroArreglo(t[1], t[2])
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>VALOR -> '+str(t[1])+' ACCESOS</td>'
    gramatical += '<td>VALOR.val = RegistroArreglo(' + \
        str(t[1])+', ACCESOS.val)</td>'
    gramatical += '</tr>'


def p_accesos_lista(t):
    'accesos    :   accesos acceso'
    t[1].append(t[2])
    t[0] = t[1]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ACCESOS -> ACCESOS ACCESO</td>'
    gramatical += '<td>ACCESOS.APPEND(ACCESO); ACCESOS.val = ACCESOS.val</td>'
    gramatical += '</tr>'


def p_accesos_acceso(t):
    'accesos    :   acceso'
    t[0] = [t[1]]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ACCESOS -> ACCESO</td>'
    gramatical += '<td>ACCESOS.val = ACCESO.val</td>'
    gramatical += '</tr>'


def p_acceso(t):
    'acceso     :   corcheteAbre expresion corcheteCierra'
    t[0] = t[2]
    global gramatical
    gramatical += '<tr>'
    gramatical += '<td>ACCESO -> [ EXPRESION ]</td>'
    gramatical += '<td>ACCESO.val = EXPRESION.val</td>'
    gramatical += '</tr>'


def p_error(t):
    if not t:
        return
    mostrarError("ERROR: Sintáctico en: "+str(t.value)+", línea: " +
                 str(t.lineno)+", columna: "+str(find_column(input_, t))+".")
    erroresSintacticos_.append(
        TError(str(t.value), str(t.lineno), str(find_column(input_, t))))
    while True:
        tok = parser.token()
        if not tok or tok.type == 'puntoComa':
            break
    parser.errok()
    return tok


def find_column(input, token):
    line_start = str(input).rfind('\n', 0, token.lexpos) + 1
    return ((token.lexpos - line_start) + 1)


def mostrarError(mensaje):
    consola_.appendPlainText(mensaje)
    cursorTemporal = consola_.textCursor()
    cursorTemporal.setPosition(len(consola_.toPlainText()))
    consola_.setTextCursor(cursorTemporal)


parser = yacc.yacc()


def parse(entrada, erroresLexicos, erroresSintacticos, consola):
    global input_, lexer, parser, consola_, erroresLexicos_, erroresSintacticos_, gramatical
    consola_ = consola
    input_ = entrada
    erroresLexicos_ = erroresLexicos
    erroresSintacticos_ = erroresSintacticos
    lexer = lex.lex()
    parser = yacc.yacc()
    return parser.parse(entrada)
