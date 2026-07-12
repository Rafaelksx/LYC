# Tema 4: Análisis Léxico - Autómatas y Metacompiladores (`Flex`)
## Universidad Nacional Experimental de Guayana
### Vicerrectorado Académico — Coordinación General de Pregrado
#### Lenguajes y Compiladores - Sección 01

* **Profesor:** Msc. Félix Márquez (`fmarquez@e.uneg.edu.ve`)
* **Integrantes del Equipo:** Fernando Centeno, Juan Longart, Adrian Reina y Rafael Rodriguez
* **Ciudad Guayana, Julio de 2026** — Período Lectivo 2026-I

---

## 📋 Descripción General del Repositorio

En este repositorio se entrega el desarrollo integral teórico-práctico del **Tema 4: Análisis Léxico**, el cual materializa los conceptos de las máquinas teóricas (Autómatas Finitos y de Pila) vinculados con las Gramáticas de Libre Contexto (GLC). En particular, se implementa la fase inicial del compilador: el **Analizador Léxico (`Lexer`)**, construyéndolo bajo dos enfoques fundamentales:
1. **Desde "cero" utilizando Python y Expresiones Regulares puras (`re`)** para la verificación de archivos `Dockerfile`.
2. **Utilizando un Metacompilador (`Flex`)** para generar automáticamente el analizador en C de un subconjunto del lenguaje **Rust (`MiniRust`)** y prototipos para Ciberseguridad.

---

## 🗂️ Estructura del Repositorio (`Tema4/`)

```text
Tema4/
│
├── 📑 INFORME_TEMA4.md                     # Informe final maestro con todas las actividades resueltas
├── 📖 README.md                            # Guía principal y manual del repositorio (este archivo)
├── 📄 tema 4.pdf                           # Documento oficial con la asignación del tema
├── 🖥️ presentacion_tema4.html              # Presentación interactiva en HTML con estilo Claymorphism y SVG puros
├── 🎙️ GUION_DEFENSA_EQUIPO.md              # Guión oficial cronometrado para los 4 integrantes (Fernando, Juan, Adrian, Rafael)
│
├── 📂 actividad1_automatas_pila/           # Actividad 1: Autómatas de Pila (PDA)
│   └── teoria_y_ejemplos.md                # Definición formal, ejemplos (a^n b^n, palíndromos) y utilidades
│
├── 📂 actividad2_dockerfile_lexer/         # Actividad 2: Lexer en Python para Dockerfile (Desde Cero)
│   ├── dockerfile_lexer.py                 # Analizador léxico motor de tokenización por regex
│   ├── run_dockerfile_lexer.py             # Script demostrativo de ejecución sobre los 3 ejemplos
│   ├── Dockerfile_ejemplo1                 # Ejemplo 1: Imagen Node.js estándar
│   ├── Dockerfile_ejemplo2                 # Ejemplo 2: Multi-stage build y directivas avanzadas
│   ├── Dockerfile_ejemplo3_errores         # Ejemplo 3: Detección y rechazo por errores léxicos intencionales
│   └── documentacion_dockerfile_lexer.md # Explicación técnica, alfabeto, regex y manual
│
├── 📂 actividad3_rust_lexer_flex/          # Actividad 3: Subconjunto de Rust (MiniRust) con Flex
│   ├── rust_lexer.l                        # Archivo de especificación Flex para MiniRust
│   ├── rust_lexer_py.py                    # Emulador en Python del lexer de MiniRust (para pruebas sin GCC)
│   ├── ejemplo_rust1.rs                    # Programa de prueba 1 válido en MiniRust
│   ├── ejemplo_rust2_errores.rs            # Programa de prueba 2 con errores léxicos
│   └── documentacion_y_manual_flex.md      # Manual de Flex, descripción de MiniRust y guía de instalación
│
└── 📂 actividad4_seguridad_informatica/    # Actividad 4: Flex aplicado a Seguridad Informática
    ├── flex_en_seguridad.md                # Indagación profunda (IDS Snort, WAF ModSecurity, YARA)
    └── yara_lexer_demo.l                   # Especificación demostrativa en Flex para reglas YARA
```

---

## 🚀 Guía Rápida de Ejecución de las Actividades

### ¿Esta actividad requiere tener instalado Docker?
> [!IMPORTANT]
> **NO, no se requiere tener instalado Docker.** El analizador léxico de la Actividad 2 inspecciona los archivos de texto (`Dockerfile`) carácter por carácter para verificar y tokenizar su sintaxis gramatical mediante expresiones regulares en Python, sin interactuar con ningún motor de contenedores ni requerir compilación de imágenes.

### 1️⃣ Ejecutar el Analizador Léxico de Dockerfile (`Actividad 2`)
Desde tu terminal (en Windows, Linux o Mac), ingresa a la carpeta `actividad2_dockerfile_lexer` y ejecuta el script de demostración con Python:
```bash
cd actividad2_dockerfile_lexer
python run_dockerfile_lexer.py
```
*Esto procesará automáticamente `Dockerfile_ejemplo1`, `Dockerfile_ejemplo2` y `Dockerfile_ejemplo3_errores`, mostrando en consola la tabla de tokens formateada y reportando el error léxico exacto (`ERROR LÉXICO en línea 7, columna 28: Carácter o secuencia no reconocida '¿'`) en el tercer archivo.*

---

### 2️⃣ Ejecutar y Probar el Analizador de MiniRust (`Actividad 3`)

#### Opción A: Probar de inmediato con Python (Sin necesidad de compilar C en Windows)
Hemos incluido `rust_lexer_py.py` que emula exactamente las reglas de `rust_lexer.l`:
```bash
cd actividad3_rust_lexer_flex
python rust_lexer_py.py ejemplo_rust1.rs
python rust_lexer_py.py ejemplo_rust2_errores.rs
```

#### Opción B: Compilación nativa con Flex y GCC (Linux / WSL / MSYS2)
1. Generar el código C con Flex:
   ```bash
   flex rust_lexer.l
   ```
2. Compilar con GCC:
   ```bash
   gcc lex.yy.c -o analizador_rust
   ```
3. Ejecutar sobre los archivos de prueba en MiniRust:
   ```bash
   ./analizador_rust ejemplo_rust1.rs
   ```

---
*Todos los códigos fuente son 100% legibles, comentados y listos para su defensa e inspección académica por el profesor Msc. Félix Márquez.*
