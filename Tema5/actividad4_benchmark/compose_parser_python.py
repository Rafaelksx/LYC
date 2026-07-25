#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actividad 4 - Tema 5: Análisis Sintáctico
Parser de archivos docker-compose.yml en Python
Universidad Nacional Experimental de Guayana (UNEG) - Lenguajes y Compiladores

Este parser analiza la estructura sintáctica de archivos docker-compose.yml
usando análisis descendente recursivo sobre la estructura YAML simplificada.
"""

import re
import time
import sys
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────
# 1. DEFINICIÓN DE TOKENS
# ─────────────────────────────────────────────────────────────
TOKEN_PATTERNS = [
    ("VERSION",    r'^version\s*:'),
    ("SERVICES",   r'^services\s*:'),
    ("NETWORKS",   r'^networks\s*:'),
    ("VOLUMES",    r'^volumes\s*:'),
    ("IMAGE",      r'^\s{2,}image\s*:'),
    ("BUILD",      r'^\s{2,}build\s*:'),
    ("PORTS",      r'^\s{2,}ports\s*:'),
    ("ENVIRONMENT",r'^\s{2,}environment\s*:'),
    ("DEPENDS_ON", r'^\s{2,}depends_on\s*:'),
    ("COMMAND",    r'^\s{2,}command\s*:'),
    ("RESTART",    r'^\s{2,}restart\s*:'),
    ("SERVICE_NAME",r'^\s{2}[a-zA-Z0-9_\-]+\s*:'),
    ("LIST_ITEM",  r'^\s+-\s+.+'),
    ("KEY_VALUE",  r'^\s+[a-zA-Z0-9_\-]+\s*:.*'),
    ("COMMENT",    r'^\s*#.*'),
    ("BLANK",      r'^\s*$'),
    ("UNKNOWN",    r'^.+'),
]

COMPILED_PATTERNS = [(name, re.compile(pat, re.MULTILINE)) for name, pat in TOKEN_PATTERNS]


@dataclass
class Token:
    tipo: str
    valor: str
    linea: int


@dataclass
class NodoAST:
    tipo: str
    valor: str = ""
    hijos: list = field(default_factory=list)

    def __repr__(self, nivel=0):
        indent = "  " * nivel
        resultado = f"{indent}[{self.tipo}] {self.valor!r}\n"
        for hijo in self.hijos:
            resultado += hijo.__repr__(nivel + 1)
        return resultado


# ─────────────────────────────────────────────────────────────
# 2. LEXER
# ─────────────────────────────────────────────────────────────
def tokenizar(contenido: str) -> list[Token]:
    tokens = []
    for num_linea, linea in enumerate(contenido.splitlines(), 1):
        matched = False
        for nombre, patron in COMPILED_PATTERNS:
            if patron.match(linea):
                if nombre not in ("COMMENT", "BLANK"):
                    tokens.append(Token(nombre, linea.strip(), num_linea))
                matched = True
                break
        if not matched:
            tokens.append(Token("UNKNOWN", linea.strip(), num_linea))
    return tokens


# ─────────────────────────────────────────────────────────────
# 3. PARSER DESCENDENTE RECURSIVO
# ─────────────────────────────────────────────────────────────
class ParserDockerCompose:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errores = []
        self.warnings = []

    def actual(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado: str = None) -> Optional[Token]:
        tok = self.actual()
        if tok is None:
            return None
        if tipo_esperado and tok.tipo != tipo_esperado:
            self.errores.append(
                f"Línea {tok.linea}: Se esperaba '{tipo_esperado}' pero se encontró '{tok.tipo}' → '{tok.valor}'"
            )
        self.pos += 1
        return tok

    def parsear(self) -> NodoAST:
        """Punto de entrada: parsea el documento completo."""
        raiz = NodoAST("DockerCompose")

        # Verificar si existe la directiva version
        if self.actual() and self.actual().tipo == "VERSION":
            tok = self.consumir("VERSION")
            version_val = tok.valor.split(":", 1)[1].strip().strip("'\"") if ":" in tok.valor else "?"
            raiz.hijos.append(NodoAST("Version", version_val))
        else:
            self.warnings.append("Advertencia: No se encontró directiva 'version'. "
                                  "Es recomendable especificar la versión del formato.")

        # Parsear secciones principales
        while self.actual() is not None:
            tok = self.actual()
            if tok.tipo == "SERVICES":
                raiz.hijos.append(self.parsear_servicios())
            elif tok.tipo == "NETWORKS":
                raiz.hijos.append(self.parsear_seccion_simple("Redes"))
            elif tok.tipo == "VOLUMES":
                raiz.hijos.append(self.parsear_seccion_simple("Volúmenes"))
            else:
                # Token no esperado a nivel raíz
                self.errores.append(
                    f"Línea {tok.linea}: Token inesperado '{tok.tipo}' → '{tok.valor}' a nivel raíz."
                )
                self.pos += 1

        return raiz

    def parsear_servicios(self) -> NodoAST:
        self.consumir("SERVICES")
        nodo_services = NodoAST("Servicios")
        # Parsear cada servicio
        while self.actual() and self.actual().tipo == "SERVICE_NAME":
            nodo_services.hijos.append(self.parsear_un_servicio())
        return nodo_services

    def parsear_un_servicio(self) -> NodoAST:
        tok = self.consumir("SERVICE_NAME")
        nombre = tok.valor.rstrip(":")
        nodo_srv = NodoAST("Servicio", nombre)

        directivas_servicio = {
            "IMAGE", "BUILD", "PORTS", "ENVIRONMENT",
            "DEPENDS_ON", "COMMAND", "RESTART", "KEY_VALUE", "LIST_ITEM"
        }

        while self.actual() and self.actual().tipo in directivas_servicio:
            t = self.actual()
            if t.tipo in ("PORTS", "ENVIRONMENT", "DEPENDS_ON"):
                nodo_srv.hijos.append(self.parsear_lista(t.tipo))
            elif t.tipo == "IMAGE":
                tok_img = self.consumir("IMAGE")
                img_val = tok_img.valor.split(":", 1)[1].strip() if ":" in tok_img.valor else "?"
                nodo_srv.hijos.append(NodoAST("Image", img_val))
            elif t.tipo == "RESTART":
                tok_rs = self.consumir("RESTART")
                rs_val = tok_rs.valor.split(":", 1)[1].strip() if ":" in tok_rs.valor else "?"
                nodo_srv.hijos.append(NodoAST("Restart", rs_val))
            elif t.tipo == "COMMAND":
                tok_cmd = self.consumir("COMMAND")
                cmd_val = tok_cmd.valor.split(":", 1)[1].strip() if ":" in tok_cmd.valor else "?"
                nodo_srv.hijos.append(NodoAST("Command", cmd_val))
            else:
                # KEY_VALUE o LIST_ITEM genérico
                tok_kv = self.consumir()
                nodo_srv.hijos.append(NodoAST("Propiedad", tok_kv.valor))

        return nodo_srv

    def parsear_lista(self, tipo: str) -> NodoAST:
        tok_header = self.consumir(tipo)
        nodo = NodoAST(tipo.capitalize(), tok_header.valor.rstrip(":").strip())
        while self.actual() and self.actual().tipo == "LIST_ITEM":
            tok_item = self.consumir("LIST_ITEM")
            nodo.hijos.append(NodoAST("Item", tok_item.valor.lstrip("- ").strip()))
        return nodo

    def parsear_seccion_simple(self, nombre: str) -> NodoAST:
        self.consumir()
        nodo = NodoAST(nombre)
        # Las entradas de networks/volumes pueden ser SERVICE_NAME (2 espacios + nombre:)
        # KEY_VALUE (4+ espacios + clave: valor) o LIST_ITEM
        tipos_validos = {"KEY_VALUE", "LIST_ITEM", "SERVICE_NAME"}
        while self.actual() and self.actual().tipo in tipos_validos:
            tok = self.consumir()
            nodo.hijos.append(NodoAST("Entrada", tok.valor))
        return nodo


# ─────────────────────────────────────────────────────────────
# 4. FUNCIÓN PRINCIPAL DE ANÁLISIS
# ─────────────────────────────────────────────────────────────
def analizar_compose(filepath: str) -> dict:
    """Analiza un archivo docker-compose.yml y retorna métricas + AST."""
    t_inicio = time.perf_counter()

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        return {"error": f"Archivo no encontrado: {filepath}", "tiempo_ms": 0}

    tokens = tokenizar(contenido)
    parser = ParserDockerCompose(tokens)
    ast = parser.parsear()

    t_fin = time.perf_counter()
    tiempo_ms = (t_fin - t_inicio) * 1000

    return {
        "archivo": filepath,
        "lineas": contenido.count("\n") + 1,
        "tokens": len(tokens),
        "servicios": sum(1 for h in ast.hijos if h.tipo == "Servicios"),
        "errores": parser.errores,
        "warnings": parser.warnings,
        "ast": ast,
        "tiempo_ms": round(tiempo_ms, 4),
        "estado": "ACEPTADO" if not parser.errores else "RECHAZADO"
    }


# ─────────────────────────────────────────────────────────────
# 5. CLI
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    archivos = sys.argv[1:] if len(sys.argv) > 1 else ["docker-compose.yml"]

    for archivo in archivos:
        print(f"\n{'='*60}")
        print(f" Parser Python → {archivo}")
        print(f"{'='*60}")
        resultado = analizar_compose(archivo)

        if "error" in resultado:
            print(f"  ❌ {resultado['error']}")
            continue

        print(f"  Líneas      : {resultado['lineas']}")
        print(f"  Tokens      : {resultado['tokens']}")
        print(f"  Errores     : {len(resultado['errores'])}")
        print(f"  Warnings    : {len(resultado['warnings'])}")
        print(f"  Tiempo      : {resultado['tiempo_ms']} ms")
        print(f"  Estado      : {resultado['estado']}")

        if resultado['errores']:
            print("\n  Errores encontrados:")
            for err in resultado['errores']:
                print(f"    ⚠ {err}")

        print(f"\n  AST generado:\n{resultado['ast']}")
