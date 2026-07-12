#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de demostración para ejecutar y validar los 3 ejemplos de Dockerfile
con el Analizador Léxico desarrollado en Python.
"""

import os
from dockerfile_lexer import analizar_archivo, imprimir_tabla_tokens

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ejemplos = [
        "Dockerfile_ejemplo1",
        "Dockerfile_ejemplo2",
        "Dockerfile_ejemplo3_errores"
    ]
    
    print("\n" + "="*78)
    print(" DEMOSTRACIÓN DEL ANALIZADOR LÉXICO PARA ARCHIVOS DOCKERFILE (PYTHON)")
    print(" Universidad Nacional Experimental de Guayana (UNEG) - Tema 4")
    print("="*78 + "\n")
    
    for ejemplo in ejemplos:
        filepath = os.path.join(base_dir, ejemplo)
        print(f"\n>>> Procesando archivo: {ejemplo} <<<")
        tokens, err = analizar_archivo(filepath, ignore_comments=False)
        imprimir_tabla_tokens(tokens, filepath, err)

if __name__ == '__main__':
    main()
