#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador Léxico en Python para MiniRust (Alternativa / Equivalente a rust_lexer.l de Flex)
-----------------------------------------------------------------------------------------
Permite verificar y demostrar la tokenización exacta del subconjunto de Rust en entornos
donde Flex/GCC no están instalados de forma nativa (ej. Windows estándar sin MSYS2).
"""

import re
import sys
import os

MINIRUST_TOKENS = [
    # 1. Comentarios
    ('COMMENT_LINE', r'//.*'),
    ('COMMENT_BLOCK', r'/\*.*?\*/'),
    
    # 2. Palabras clave del subconjunto (Keywords)
    ('KEYWORD', r'\b(?:fn|let|mut|if|else|while|for|in|return|true|false)\b'),
    ('MACRO', r'\bprintln!\b'),
    
    # 3. Tipos de datos primitivos
    ('TYPE', r'\b(?:i32|f64|bool|char|String)\b'),
    
    # 4. Operadores multicarácter
    ('OP_MULTI', r'==|!=|<=|>=|&&|\|\||->|\.\.|\+=|-='),
    
    # 5. Operadores de un solo carácter
    ('OP_SINGLE', r'[+\-*/%=<>!&]'),
    
    # 6. Delimitadores
    ('DELIMITER', r'[(){}\[\]:;,.]'),
    
    # 7. Literales y Cadenas
    ('LIT_FLOAT', r'\b\d+\.\d+\b'),
    ('LIT_INT', r'\b\d+\b'),
    ('LIT_STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),
    
    # 8. Identificadores
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    
    # 9. Control de espacios y saltos de línea
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t\r]+'),
    
    # 10. Caracteres desconocidos / Error
    ('MISMATCH', r'.'),
]

REGEX_MINIRUST = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in MINIRUST_TOKENS), re.DOTALL | re.MULTILINE)

def tokenizar_minirust(codigo: str):
    line_num = 1
    line_start = 0
    tokens = []
    
    for mo in REGEX_MINIRUST.finditer(codigo):
        kind = mo.lastgroup
        value = mo.group(kind)
        col = mo.start() - line_start + 1
        
        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'COMMENT_LINE':
            continue
        elif kind == 'COMMENT_BLOCK':
            line_num += value.count('\n')
            if '\n' in value:
                line_start = mo.start() + value.rfind('\n') + 1
            continue
        elif kind == 'MISMATCH':
            print(f"\n[!] ERROR LÉXICO CRÍTICO en Línea {line_num}, Columna {col}: Carácter no reconocido '{value}'\n")
            continue
        
        # Mapear nombres a formato Flex
        if kind == 'KEYWORD':
            token_type = f"TK_KEYWORD_{value.upper()}"
        elif kind == 'MACRO':
            token_type = "TK_MACRO_PRINTLN"
        elif kind == 'TYPE':
            token_type = f"TK_TYPE_{value.upper()}"
        elif kind in ('LIT_FLOAT', 'LIT_INT', 'LIT_STRING'):
            token_type = f"TK_{kind}"
        elif kind == 'IDENTIFIER':
            token_type = "TK_IDENTIFICADOR"
        elif kind in ('OP_MULTI', 'OP_SINGLE'):
            token_type = f"TK_OPERATOR_{value}"
        elif kind == 'DELIMITER':
            token_type = f"TK_DELIM_{value}"
        else:
            token_type = kind
            
        tokens.append((token_type, value, line_num, col))
        
    return tokens

def main():
    if len(sys.argv) < 2:
        print("Uso: python rust_lexer_py.py <archivo.rs>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: No se encontró {filepath}")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        codigo = f.read()
        
    print("="*78)
    print(f" ANÁLISIS LÉXICO MINIRUST (EMULADOR PYTHON) - Archivo: {filepath}")
    print("="*78)
    print(f"{'TIPO DE TOKEN':<22} | {'LEXEMA (VALOR)':<30} | {'LÍNEA':<6} | {'COLUMNA':<7}")
    print("-" * 78)
    
    toks = tokenizar_minirust(codigo)
    for t_type, val, line, col in toks:
        print(f"{t_type:<22} | {val:<30} | {line:<6} | {col:<7}")
    print("="*78 + "\n")

if __name__ == '__main__':
    main()
