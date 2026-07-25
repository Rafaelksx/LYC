#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actividad 5 – Tema 5: Análisis Sintáctico
UnegScript Hybrid Parser: Asistente Léxico-Sintáctico con IA simulada
Universidad Nacional Experimental de Guayana (UNEG) - Lenguajes y Compiladores

DESCRIPCIÓN:
  Este parser hibrido para un subconjunto de Python ("UnegScript") implementa:
  1. LEXER  → Tokenización con cálculo de distancia Levenshtein para detectar
              palabras clave con errores tipográficos (ej. pront → print).
  2. PARSER → Análisis Descendente Recursivo con lookahead de 1 token y
              recuperación de errores por pánico (modo sync).
  3. MOCK IA → Si la confianza del lexer cae por debajo del umbral (< 0.80),
               se consulta un "LLM Simulado" (diccionario de correcciones)
               que actúa como fallback inteligente.
"""

import re
import difflib
import sys
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 1: TABLA DE PALABRAS CLAVE Y TOKENS (VOCABULARIO LÉXICO)
# ═══════════════════════════════════════════════════════════════

PALABRAS_CLAVE = {
    "print", "if", "else", "elif", "while", "for",
    "in", "return", "def", "class", "import", "from",
    "and", "or", "not", "True", "False", "None",
    "break", "continue", "pass", "try", "except", "finally",
    "with", "as", "lambda", "yield", "del", "global",
}

TOKEN_PATTERNS = [
    # Números flotantes y enteros
    ("FLOAT",    r'\d+\.\d+'),
    ("INT",      r'\d+'),
    # Cadenas (comillas dobles y simples, multilínea básica)
    ("STRING",   r'"[^"]*"|\'[^\']*\''),
    # Operadores de dos caracteres (PRIMERO, para no confundir con los de uno)
    ("OP",       r'==|!=|<=|>=|->|\+=|-=|\*=|/=|//|and\b|or\b|not\b'),
    # Identificadores / palabras clave
    ("ID",       r'[a-zA-Z_][a-zA-Z0-9_]*'),
    # Operadores de un carácter
    ("OP",       r'[+\-*/=<>!%&|^~@]'),
    # Delimitadores
    ("LPAREN",   r'\('),
    ("RPAREN",   r'\)'),
    ("LBRACE",   r'\{'),
    ("RBRACE",   r'\}'),
    ("LBRACKET", r'\['),
    ("RBRACKET", r'\]'),
    ("COLON",    r':'),
    ("SEMICOLON",r';'),
    ("COMMA",    r','),
    ("DOT",      r'\.'),
    # Ignorar espacios y comentarios
    ("SKIP",     r'[ \t]+|#[^\n]*'),
    ("NEWLINE",  r'\n'),
    ("UNKNOWN",  r'.'),
]

TOKEN_REGEX = re.compile(
    '|'.join(f'(?P<{name}_{i}>{pattern})' for i, (name, pattern) in enumerate(TOKEN_PATTERNS))
)

# ═══════════════════════════════════════════════════════════════
# SECCIÓN 2: MOCK LLM (IA SIMULADA)
# ═══════════════════════════════════════════════════════════════
class MockLLM:
    """
    Simula la respuesta de un Large Language Model (LLM) para corrección de código.
    En un sistema real, este método haría una llamada a la API de OpenAI/Gemini.
    En esta implementación, utiliza una base de conocimiento curada de errores comunes.
    """
    BASE_CONOCIMIENTO = {
        # Funciones built-in comunes
        "pront":     ("print",   "La función de impresión en Python es 'print'"),
        "prnt":      ("print",   "La función de impresión en Python es 'print'"),
        "pritn":     ("print",   "Posible error tipográfico: ¿quisiste decir 'print'?"),
        "prrint":    ("print",   "Posible error tipográfico: ¿quisiste decir 'print'?"),
        "inpt":      ("input",   "La función de entrada es 'input'"),
        "imput":     ("input",   "La función de entrada es 'input'"),
        "lenght":    ("len",     "La función de longitud es 'len'"),
        "ragne":     ("range",   "La función de rango es 'range'"),
        "rang":      ("range",   "La función de rango es 'range'"),
        # Palabras clave
        "whlie":     ("while",   "La palabra clave es 'while'"),
        "wile":      ("while",   "La palabra clave es 'while'"),
        "fro":       ("for",     "La palabra clave es 'for'"),
        "iff":       ("if",      "La palabra clave es 'if'"),
        "esle":      ("else",    "La palabra clave es 'else'"),
        "retrun":    ("return",  "La palabra clave es 'return'"),
        "reutrn":    ("return",  "La palabra clave es 'return'"),
        "impot":     ("import",  "La palabra clave es 'import'"),
        "fals":      ("False",   "El literal booleano es 'False'"),
        "treu":      ("True",    "El literal booleano es 'True'"),
        # Conceptos más complejos
        "funcion":   ("def",     "En Python, las funciones se definen con 'def'"),
        "funcion":   ("def",     "En Python, las funciones se definen con 'def'"),
        "clase":     ("class",   "En Python, las clases se definen con 'class'"),
        "entonces":  (":",       "En Python, los bloques se abren con ':'"),
    }

    def corregir(self, token_erroneo: str, confianza: float, contexto: str = "") -> dict:
        """
        Consulta la base de conocimiento y retorna una sugerencia de corrección.
        Simula una llamada a un LLM real con latencia de red cero (demo local).
        """
        token_lower = token_erroneo.lower()

        # Búsqueda directa en la base de conocimiento
        if token_lower in self.BASE_CONOCIMIENTO:
            correccion, explicacion = self.BASE_CONOCIMIENTO[token_lower]
            return {
                "original": token_erroneo,
                "sugerencia": correccion,
                "confianza_ia": 0.98,
                "explicacion": explicacion,
                "fuente": "Mock-LLM (Base de Conocimiento Curada)"
            }

        # Fallback: búsqueda aproximada por Levenshtein en la base de conocimiento
        claves = list(self.BASE_CONOCIMIENTO.keys())
        matches = difflib.get_close_matches(token_lower, claves, n=1, cutoff=0.6)
        if matches:
            correccion, explicacion = self.BASE_CONOCIMIENTO[matches[0]]
            return {
                "original": token_erroneo,
                "sugerencia": correccion,
                "confianza_ia": 0.75,
                "explicacion": f"[Aproximado] {explicacion}",
                "fuente": "Mock-LLM (Levenshtein sobre KB)"
            }

        return {
            "original": token_erroneo,
            "sugerencia": token_erroneo,
            "confianza_ia": 0.0,
            "explicacion": "No se encontró una corrección conocida.",
            "fuente": "Mock-LLM (Sin sugerencia)"
        }


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 3: LEXER HÍBRIDO CON LEVENSHTEIN
# ═══════════════════════════════════════════════════════════════
UMBRAL_CONFIANZA = 0.85  # Tokens con similitud Levenshtein <= 85% se envían al Mock-LLM

@dataclass
class Token:
    tipo: str
    valor: str
    linea: int
    col: int
    confianza: float = 1.0
    sugerencia: Optional[str] = None
    nota_ia: Optional[str] = None


def calcular_confianza(identificador: str) -> tuple[float, Optional[str]]:
    """
    Calcula la similitud entre un identificador y las palabras clave conocidas.
    Retorna (confianza, mejor_coincidencia_o_None).

    Estrategia:
    - Si el identificador ES exactamente una palabra clave → (1.0, None).
    - Si es similar a una keyword (60-99% similitud) → (ratio, sugerencia).
      Esto detecta errores tipográficos como 'pront'→'print' (ratio ≈0.80).
    - Si es un identificador de usuario sin parecido → (1.0, None) sin sugerencia.

    NOTA: Para evitar falsos positivos en identificadores largos como 'calcular'
    o 'resultado', usamos cutoff=0.62 y solo flagueamos si el token tiene
    una longitud similar a la keyword (diferencia máxima de 3 caracteres).
    """
    if identificador in PALABRAS_CLAVE:
        return 1.0, None

    coincidencias = difflib.get_close_matches(
        identificador,
        PALABRAS_CLAVE,
        n=1,
        cutoff=0.62  # Solo sugiere si la similitud supera el 62%
    )

    if coincidencias:
        mejor = coincidencias[0]
        # Evitar falsos positivos: solo flagear si las longitudes son similares
        if abs(len(identificador) - len(mejor)) <= 3:
            similitud = difflib.SequenceMatcher(None, identificador, mejor).ratio()
            return similitud, mejor

    return 1.0, None  # Es un identificador de usuario válido


def tokenizar(codigo: str, llm: MockLLM) -> list[Token]:
    """
    Tokeniza el código fuente aplicando Levenshtein y consultando el Mock-LLM
    cuando la confianza cae por debajo de UMBRAL_CONFIANZA.
    """
    tokens = []
    linea_actual = 1
    inicio_linea = 0

    for mo in TOKEN_REGEX.finditer(codigo):
        tipo_raw = mo.lastgroup   # Ej: 'ID_4', 'INT_0'
        tipo = tipo_raw.rsplit("_", 1)[0]  # Normalizar: 'ID_4' → 'ID'
        valor = mo.group()
        col = mo.start() - inicio_linea + 1

        if tipo == "SKIP":
            continue
        elif tipo == "NEWLINE":
            linea_actual += 1
            inicio_linea = mo.end()
            continue
        elif tipo == "UNKNOWN":
            tokens.append(Token("ERROR_LÉXICO", valor, linea_actual, col, 0.0,
                                nota_ia=f"Carácter no reconocido: '{valor}'"))
            continue

        # ── Verificación de confianza para identificadores ──
        if tipo == "ID":
            # Si coincide con una keyword, la clasificamos como tal
            if valor in PALABRAS_CLAVE:
                tokens.append(Token("KEYWORD", valor, linea_actual, col, 1.0))
                continue

            confianza, sugerencia = calcular_confianza(valor)

            if sugerencia is not None and confianza <= UMBRAL_CONFIANZA:
                # ¡Confianza baja! Consultar el Mock-LLM
                respuesta_ia = llm.corregir(valor, confianza, contexto=codigo)
                tok = Token(
                    tipo="ID_POSIBLE_ERROR",
                    valor=valor,
                    linea=linea_actual,
                    col=col,
                    confianza=confianza,
                    sugerencia=respuesta_ia["sugerencia"],
                    nota_ia=f"[IA] {respuesta_ia['explicacion']} "
                            f"(confianza Levenshtein: {confianza:.0%}, "
                            f"confianza IA: {respuesta_ia['confianza_ia']:.0%})"
                )
                tokens.append(tok)
                continue

        tokens.append(Token(tipo, valor, linea_actual, col))

    return tokens


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 4: NODOS DEL AST
# ═══════════════════════════════════════════════════════════════
@dataclass
class NodoAST:
    tipo: str
    valor: str = ""
    hijos: list = field(default_factory=list)

    def __repr__(self, nivel: int = 0) -> str:
        indent = "  " * nivel
        s = f"{indent}[{self.tipo}]"
        if self.valor:
            s += f" {self.valor!r}"
        s += "\n"
        for hijo in self.hijos:
            s += hijo.__repr__(nivel + 1)
        return s


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 5: PARSER DESCENDENTE RECURSIVO
# ═══════════════════════════════════════════════════════════════
class UnegScriptParser:
    """
    Parser de análisis descendente recursivo LL(1) para un subconjunto
    de Python (UnegScript). Implementa recuperación de errores en modo pánico.
    """
    TOKENS_SINCRONIZACION = {"SEMICOLON", "NEWLINE", "KEYWORD"}

    def __init__(self, tokens: list[Token]):
        # Filtrar tokens de error para análisis (los reportamos pero no paramos)
        self.tokens = [t for t in tokens if t.tipo not in ("ERROR_LÉXICO",)]
        self.tokens_errores_lexicos = [t for t in tokens if t.tipo == "ERROR_LÉXICO"]
        self.pos = 0
        self.errores_sintacticos = []
        self.advertencias = []

    def actual(self) -> Optional[Token]:
        while self.pos < len(self.tokens) and self.tokens[self.pos].tipo == "NEWLINE":
            self.pos += 1
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self) -> Optional[Token]:
        tok = self.actual()
        if tok:
            self.pos += 1
        return tok

    def esperar(self, tipo: str = None, valor: str = None) -> Optional[Token]:
        tok = self.actual()
        if tok is None:
            self.errores_sintacticos.append("Fin de archivo inesperado.")
            return None
        if tipo and tok.tipo != tipo:
            self.errores_sintacticos.append(
                f"Línea {tok.linea}, Col {tok.col}: Se esperaba tipo '{tipo}' "
                f"pero se encontró '{tok.tipo}' → '{tok.valor}'"
            )
            self._sincronizar()
            return None
        if valor and tok.valor != valor:
            self.errores_sintacticos.append(
                f"Línea {tok.linea}, Col {tok.col}: Se esperaba '{valor}' "
                f"pero se encontró '{tok.valor}'"
            )
            self._sincronizar()
            return None
        return self.consumir()

    def _sincronizar(self):
        """Modo pánico: descarta tokens hasta encontrar un token de sincronización."""
        while self.actual() and self.actual().tipo not in self.TOKENS_SINCRONIZACION:
            self.pos += 1
        if self.actual() and self.actual().tipo == "SEMICOLON":
            self.pos += 1  # Consumir el ';' de recuperación

    # ──────────────────────────────────────────────────────────
    # Reglas de la gramática
    # ──────────────────────────────────────────────────────────
    def parsear(self) -> NodoAST:
        raiz = NodoAST("Programa")
        while self.actual() is not None:
            nodo = self.parsear_sentencia()
            if nodo:
                raiz.hijos.append(nodo)
        return raiz

    def parsear_sentencia(self) -> Optional[NodoAST]:
        tok = self.actual()
        if tok is None:
            return None

        if tok.tipo == "KEYWORD":
            if tok.valor == "print":
                return self.parsear_print()
            elif tok.valor == "if":
                return self.parsear_if()
            elif tok.valor == "while":
                return self.parsear_while()
            elif tok.valor == "for":
                return self.parsear_for()
            elif tok.valor == "def":
                return self.parsear_def()
            elif tok.valor == "return":
                return self.parsear_return()
            else:
                self.consumir()
                return NodoAST("Keyword", tok.valor)

        elif tok.tipo == "ID":
            return self.parsear_asignacion_o_llamada()

        elif tok.tipo == "ID_POSIBLE_ERROR":
            # Registrar advertencia y tratar el token sugerido
            nota = tok.nota_ia or f"Posible error tipográfico: '{tok.valor}' → '{tok.sugerencia}'"
            self.advertencias.append(f"Línea {tok.linea}, Col {tok.col}: {nota}")
            # Intentar corregir y continuar
            tok_corregido = Token("ID", tok.sugerencia or tok.valor, tok.linea, tok.col)
            self.tokens[self.pos] = tok_corregido
            return self.parsear_sentencia()

        elif tok.tipo == "SEMICOLON":
            self.consumir()
            return None

        else:
            return self.parsear_expresion()

    def parsear_print(self) -> NodoAST:
        self.consumir()  # 'print'
        nodo = NodoAST("Print")
        if self.actual() and self.actual().tipo == "LPAREN":
            self.consumir()  # '('
            nodo.hijos.append(self.parsear_expresion())
            if self.actual() and self.actual().tipo == "RPAREN":
                self.consumir()  # ')'
            else:
                self.errores_sintacticos.append("Se esperaba ')' para cerrar print(...).")
        return nodo

    def parsear_if(self) -> NodoAST:
        self.consumir()  # 'if'
        nodo_if = NodoAST("If")
        # Condición
        condicion = self.parsear_expresion()
        nodo_if.hijos.append(NodoAST("Condicion", hijos=[condicion] if condicion else []))
        # ':' esperado
        if self.actual() and self.actual().valor == ":":
            self.consumir()
        # Cuerpo
        cuerpo = NodoAST("Cuerpo")
        while self.actual() and not (
            self.actual().tipo == "KEYWORD" and self.actual().valor in ("else", "elif")
        ):
            s = self.parsear_sentencia()
            if s:
                cuerpo.hijos.append(s)
            if self.actual() is None:
                break
        nodo_if.hijos.append(cuerpo)
        # else / elif opcionales
        if self.actual() and self.actual().tipo == "KEYWORD" and self.actual().valor == "else":
            self.consumir()
            if self.actual() and self.actual().valor == ":":
                self.consumir()
            nodo_else = NodoAST("Else")
            s = self.parsear_sentencia()
            if s:
                nodo_else.hijos.append(s)
            nodo_if.hijos.append(nodo_else)
        return nodo_if

    def parsear_while(self) -> NodoAST:
        self.consumir()  # 'while'
        nodo = NodoAST("While")
        condicion = self.parsear_expresion()
        nodo.hijos.append(NodoAST("Condicion", hijos=[condicion] if condicion else []))
        if self.actual() and self.actual().valor == ":":
            self.consumir()
        cuerpo = NodoAST("Cuerpo")
        while self.actual() and not (self.actual().tipo == "KEYWORD" and self.actual().valor != "while"):
            s = self.parsear_sentencia()
            if s:
                cuerpo.hijos.append(s)
            else:
                break
        nodo.hijos.append(cuerpo)
        return nodo

    def parsear_for(self) -> NodoAST:
        self.consumir()  # 'for'
        nodo = NodoAST("For")
        var = self.consumir()
        nodo.hijos.append(NodoAST("Variable", var.valor if var else "?"))
        if self.actual() and self.actual().valor == "in":
            self.consumir()
        iterable = self.parsear_expresion()
        nodo.hijos.append(NodoAST("Iterable", hijos=[iterable] if iterable else []))
        if self.actual() and self.actual().valor == ":":
            self.consumir()
        return nodo

    def parsear_def(self) -> NodoAST:
        self.consumir()  # 'def'
        nodo = NodoAST("FuncDef")
        nombre = self.consumir()
        nodo.valor = nombre.valor if nombre else "?"
        if self.actual() and self.actual().tipo == "LPAREN":
            self.consumir()
            params = NodoAST("Params")
            while self.actual() and self.actual().tipo != "RPAREN":
                p = self.consumir()
                if p and p.tipo != "COMMA":
                    params.hijos.append(NodoAST("Param", p.valor))
            if self.actual() and self.actual().tipo == "RPAREN":
                self.consumir()
            nodo.hijos.append(params)
        if self.actual() and self.actual().valor == ":":
            self.consumir()
        return nodo

    def parsear_return(self) -> NodoAST:
        self.consumir()  # 'return'
        nodo = NodoAST("Return")
        expr = self.parsear_expresion()
        if expr:
            nodo.hijos.append(expr)
        return nodo

    def parsear_asignacion_o_llamada(self) -> Optional[NodoAST]:
        tok_id = self.consumir()
        siguiente = self.actual()

        if siguiente and siguiente.tipo == "OP" and siguiente.valor == "=":
            # Asignación: id = expresión
            self.consumir()  # '='
            nodo = NodoAST("Asignacion")
            nodo.hijos.append(NodoAST("ID", tok_id.valor))
            expr = self.parsear_expresion()
            if expr:
                nodo.hijos.append(expr)
            return nodo

        elif siguiente and siguiente.tipo == "LPAREN":
            # Llamada a función: id(args)
            self.consumir()  # '('
            nodo = NodoAST("Llamada", tok_id.valor)
            while self.actual() and self.actual().tipo != "RPAREN":
                arg = self.parsear_expresion()
                if arg:
                    nodo.hijos.append(arg)
                if self.actual() and self.actual().tipo == "COMMA":
                    self.consumir()
            if self.actual() and self.actual().tipo == "RPAREN":
                self.consumir()
            return nodo

        return NodoAST("ID", tok_id.valor)

    def parsear_expresion(self) -> Optional[NodoAST]:
        """Parsea una expresión simple (término [op término]*) con un nivel de profundidad."""
        izquierdo = self.parsear_termino()
        if izquierdo is None:
            return None

        operadores_binarios = {"+", "-", "*", "/", "//", "%", "==", "!=", "<", ">", "<=", ">=", "and", "or"}

        while self.actual() and self.actual().tipo == "OP" and self.actual().valor in operadores_binarios:
            op = self.consumir()
            derecho = self.parsear_termino()
            nodo_op = NodoAST("BinOp", op.valor)
            nodo_op.hijos.append(izquierdo)
            nodo_op.hijos.append(derecho or NodoAST("NULL"))
            izquierdo = nodo_op

        return izquierdo

    def parsear_termino(self) -> Optional[NodoAST]:
        tok = self.actual()
        if tok is None:
            return None

        if tok.tipo == "INT":
            self.consumir()
            return NodoAST("Entero", tok.valor)
        elif tok.tipo == "FLOAT":
            self.consumir()
            return NodoAST("Flotante", tok.valor)
        elif tok.tipo == "STRING":
            self.consumir()
            return NodoAST("Cadena", tok.valor)
        elif tok.tipo == "KEYWORD" and tok.valor in ("True", "False", "None"):
            self.consumir()
            return NodoAST("Literal", tok.valor)
        elif tok.tipo in ("ID", "ID_POSIBLE_ERROR"):
            return self.parsear_asignacion_o_llamada()
        elif tok.tipo == "KEYWORD":
            return self.parsear_sentencia()
        elif tok.tipo == "LPAREN":
            self.consumir()  # '('
            expr = self.parsear_expresion()
            if self.actual() and self.actual().tipo == "RPAREN":
                self.consumir()  # ')'
            return NodoAST("Grupo", hijos=[expr] if expr else [])
        elif tok.tipo == "OP" and tok.valor == "not":
            self.consumir()
            operando = self.parsear_termino()
            nodo = NodoAST("UnaryOp", "not")
            if operando:
                nodo.hijos.append(operando)
            return nodo

        # Token inesperado
        self.consumir()
        return None


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 6: FUNCIÓN PRINCIPAL DE ANÁLISIS
# ═══════════════════════════════════════════════════════════════
def analizar_unegscript(codigo: str, verbose: bool = True) -> dict:
    llm = MockLLM()
    tokens = tokenizar(codigo, llm)
    parser = UnegScriptParser(tokens)
    ast = parser.parsear()

    # Tokens con posibles errores tipográficos
    tokens_con_advertencia = [t for t in tokens if t.tipo == "ID_POSIBLE_ERROR"]

    resultado = {
        "tokens": tokens,
        "ast": ast,
        "errores_lexicos": parser.tokens_errores_lexicos,
        "errores_sintacticos": parser.errores_sintacticos,
        "advertencias": parser.advertencias,
        "tokens_ia": tokens_con_advertencia,
        "estado": "ACEPTADO" if not parser.errores_sintacticos and not parser.tokens_errores_lexicos else "CON ERRORES"
    }

    if verbose:
        _imprimir_reporte(codigo, resultado)

    return resultado


def _imprimir_reporte(codigo: str, r: dict):
    sep = "=" * 70
    print(f"\n{sep}")
    print("  UnegScript Hybrid Parser — UNEG | Lenguajes y Compiladores")
    print(sep)
    print(f"\n  Código analizado:\n  {'─'*50}")
    for i, linea in enumerate(codigo.strip().splitlines(), 1):
        print(f"  {i:3d} | {linea}")
    print(f"  {'─'*50}\n")

    # Errores léxicos
    if r["errores_lexicos"]:
        print("  ❌ ERRORES LÉXICOS:")
        for t in r["errores_lexicos"]:
            print(f"    Línea {t.linea}, Col {t.col}: {t.nota_ia}")

    # Advertencias de IA (tokens con posibles errores tipográficos)
    if r["advertencias"]:
        print("\n  🤖 SUGERENCIAS DE LA IA (Mock-LLM):")
        for adv in r["advertencias"]:
            print(f"    {adv}")

    # Errores sintácticos
    if r["errores_sintacticos"]:
        print("\n  ⚠ ERRORES SINTÁCTICOS:")
        for err in r["errores_sintacticos"]:
            print(f"    {err}")

    # AST
    print(f"\n  📐 AST GENERADO:")
    print(r["ast"])

    # Resumen
    print(f"\n  Estado final: {r['estado']}")
    print(f"  Tokens totales    : {len(r['tokens'])}")
    print(f"  Consultas al Mock-LLM : {len(r['tokens_ia'])}")
    print(f"  Advertencias IA   : {len(r['advertencias'])}")
    print(f"  Errores sintácticos: {len(r['errores_sintacticos'])}")
    print(sep + "\n")


# ═══════════════════════════════════════════════════════════════
# SECCIÓN 7: CASOS DE PRUEBA
# ═══════════════════════════════════════════════════════════════
CASOS_PRUEBA = {
    "Caso 1: Código correcto (sin errores)": """
x = 5
y = 10
resultado = x + y
print(resultado)
""",
    "Caso 2: Error tipográfico 'pront' y 'prnt' (del enunciado)": """
pront x = 5;
if x > 3 prnt(x) else prnt("no")
""",
    "Caso 3: Función simple con return": """
def calcular(a, b):
    resultado = a + b
    return resultado

valor = calcular(3, 7)
print(valor)
""",
    "Caso 4: Múltiples errores tipográficos": """
whlie x > 0:
    pront(x)
    x = x - 1
retrun True
""",
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo archivo: analizar el archivo pasado como argumento
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            codigo = f.read()
        analizar_unegscript(codigo)
    else:
        # Modo demo: ejecutar todos los casos de prueba
        for nombre, codigo in CASOS_PRUEBA.items():
            print(f"\n{'#'*70}")
            print(f"# TEST: {nombre}")
            print(f"{'#'*70}")
            analizar_unegscript(codigo)
