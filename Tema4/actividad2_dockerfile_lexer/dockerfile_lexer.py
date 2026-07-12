#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador Léxico (Lexer) para Archivos Docker (Dockerfile)
------------------------------------------------------------
Diseñado e implementado desde cero utilizando Expresiones Regulares (Módulo `re` de Python)
y la arquitectura de tokenización con generadores (`re.finditer`).

Permite verificar y tokenizar cualquier archivo Dockerfile, detectando:
- Directivas principales (FROM, RUN, CMD, COPY, ENV, etc.)
- Flags (--platform, --chown, --from, etc.)
- Variables de entorno ($VAR o ${VAR})
- Cadenas de texto, números/puertos, rutas e identificadores
- Comentarios y control exacto de errores léxicos por línea y columna.
"""

import re
import sys
import os
from typing import Iterator, Tuple, List, Optional

# =============================================================================
# 1. DEFINICIÓN DE EXPRESIONES REGULARES POR TOKEN
# =============================================================================
# El orden de la lista es fundamental: los patrones más específicos deben colocarse
# antes de los más generales para evitar consumos incorrectos por precedencia.

DOCKER_TOKENS = [
    # 1. Comentarios (Líneas que inician con # o contienen # precedido de espacio)
    ('COMMENT', r'^\s*#.*'),
    
    # 2. Directivas / Instrucciones de Dockerfile (insensibles a mayúsculas/minúsculas en regex)
    ('DIRECTIVE', r'\b(?:FROM|RUN|CMD|LABEL|EXPOSE|ENV|ADD|COPY|ENTRYPOINT|VOLUME|USER|WORKDIR|ARG|ONBUILD|STOPSIGNAL|HEALTHCHECK|SHELL)\b'),
    
    # 3. Flags opcionales en directivas (ej: --platform=linux/amd64, --chown=root:root, --from=builder, --interval=5s)
    ('FLAG', r'--[a-zA-Z0-9_-]+(?:=[a-zA-Z0-9_./:-]+)?'),
    
    # 4. Variables de entorno / Expansiones (ej: $PORT, ${NODE_ENV}, ${APP_DIR:-/usr/src/app})
    ('VARIABLE', r'\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]+)?\}'),
    
    # 5. Cadenas de texto delimitadas por comillas dobles o simples
    ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''),
    
    # 6. Operadores lógicos o de continuación y símbolos especiales
    ('OPERATOR', r'&&|\|\||\\|=|:|,|\[|\]|\(|\)'),
    
    # 7. Puertos (ej: 8080/tcp, 3000/udp)
    ('PORT', r'\b\d{1,5}/(?:tcp|udp)\b'),
    
    # 8. Números puros (ej: 80, 3000, 1)
    ('NUMBER', r'\b\d+\b'),
    
    # 9. Palabras/Identificadores/Rutas (nombres de imagen, etiquetas, paquetes, comandos, rutas de archivo)
    ('WORD', r'[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)*(?::[a-zA-Z0-9._-]+)?'),
    
    # 10. Saltos de línea (fundamentales para contar las líneas y las instrucciones)
    ('NEWLINE', r'\n'),
    
    # 11. Espacios en blanco y tabulaciones (que no sean saltos de línea) - Se ignoran en la tokenización
    ('SKIP', r'[ \t\r]+'),
    
    # 12. Caracteres no reconocidos - Generará un error léxico exacto
    ('MISMATCH', r'.'),
]

# Compilación de la expresión regular combinada con nombres de grupo (?P<name>pattern)
REGEX_COMBINADA = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in DOCKER_TOKENS)
COMPILED_REGEX = re.compile(REGEX_COMBINADA, re.IGNORECASE | re.MULTILINE)


# =============================================================================
# 2. MOTOR DEL ANALIZADOR LÉXICO (GENERADOR)
# =============================================================================
def dockerfile_lexer(input_text: str, ignore_comments: bool = True) -> Iterator[Tuple[str, str, int, int]]:
    """
    Analiza una cadena de texto representando un Dockerfile y genera sus tokens.
    
    Yields:
        Tuple[str, str, int, int]: (kind, value, line_num, column)
    
    Raises:
        SyntaxError: Si se encuentra un carácter no válido según el alfabeto de Dockerfile.
    """
    line_num = 1
    line_start = 0
    
    for mo in COMPILED_REGEX.finditer(input_text):
        kind = mo.lastgroup
        value = mo.group(kind)
        column = mo.start() - line_start + 1
        
        if kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'COMMENT':
            if not ignore_comments:
                yield (kind, value.strip(), line_num, column)
            continue
        elif kind == 'MISMATCH':
            # Capturamos toda la línea para dar un mensaje de error pedagógico y detallado
            lines = input_text.split('\n')
            current_line_text = lines[line_num - 1] if line_num <= len(lines) else ""
            error_msg = (
                f"\n[!] ERROR LÉXICO en línea {line_num}, columna {column}:\n"
                f"    Carácter o secuencia no reconocida: '{value}'\n"
                f"    Línea completa: >> {current_line_text.strip()} <<\n"
            )
            raise SyntaxError(error_msg)
        else:
            # Si es una directiva, la estandarizamos a mayúsculas para coherencia
            if kind == 'DIRECTIVE':
                value = value.upper()
            yield (kind, value, line_num, column)


# =============================================================================
# 3. FUNCIONES DE ANÁLISIS Y REPORTE VISUAL
# =============================================================================
def analizar_archivo(filepath: str, ignore_comments: bool = True) -> Tuple[List[Tuple[str, str, int, int]], Optional[str]]:
    """
    Lee un archivo Dockerfile, ejecuta el analizador léxico y devuelve la lista de tokens o el error.
    """
    if not os.path.exists(filepath):
        return [], f"Error: El archivo '{filepath}' no se encuentra en el sistema."
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        return [], f"Error al leer el archivo '{filepath}': {str(e)}"
    
    tokens = []
    try:
        for token in dockerfile_lexer(contenido, ignore_comments=ignore_comments):
            tokens.append(token)
        return tokens, None
    except SyntaxError as se:
        return tokens, str(se)
    except Exception as e:
        return tokens, f"Error inesperado durante el análisis: {str(e)}"


def imprimir_tabla_tokens(tokens: List[Tuple[str, str, int, int]], filepath: str, error: Optional[str] = None):
    """
    Imprime una tabla formateada con los tokens detectados en la consola.
    """
    print("=" * 78)
    print(f" RESULTADOS DEL ANÁLISIS LÉXICO DOCKERFILE: {os.path.basename(filepath)}")
    print("=" * 78)
    print(f"{'TIPO (TOKEN)':<16} | {'LEXEMA (VALOR)':<38} | {'LÍNEA':<6} | {'COLUMNA':<7}")
    print("-" * 78)
    
    for kind, value, line, col in tokens:
        # Acortar valor si es demasiado largo para la visualización en tabla
        display_val = (value[:35] + '...') if len(value) > 38 else value
        print(f"{kind:<16} | {display_val:<38} | {line:<6} | {col:<7}")
    
    print("-" * 78)
    if error:
        print(error)
        print("=" * 78)
        print(" -> ESTADO: RECHAZADO (Se encontraron errores léxicos)\n")
    else:
        print(f" -> ESTADO: ACEPTADO ({len(tokens)} tokens reconocidos exitosamente sin errores léxicos)\n")


# =============================================================================
# 4. PUNTO DE ENTRADA PRINCIPAL (CLI)
# =============================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python dockerfile_lexer.py <ruta_al_archivo_dockerfile>")
        sys.exit(1)
    
    archivo = sys.argv[1]
    toks, err = analizar_archivo(archivo, ignore_comments=False)
    imprimir_tabla_tokens(toks, archivo, err)
