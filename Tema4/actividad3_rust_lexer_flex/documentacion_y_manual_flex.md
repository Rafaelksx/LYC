# Actividad 3: Analizador Léxico para Subconjunto de Rust (`MiniRust`) usando Metacompilador `Flex`

---

## 1. Manual de Usuario del Metacompilador `Flex` (Fast Lexical Analyzer Generator)

### 1.1 ¿Qué es Flex?
**Flex** es un metacompilador o generador automático de analizadores léxicos (*lexers*). Su función principal es recibir como entrada un archivo de especificación escrito en un lenguaje especializado de reglas de expresiones regulares y acciones en C (con extensión `.l`), y generar automáticamente el código fuente en lenguaje C (`lex.yy.c`) que implementa un **Autómata Finito Determinístico (AFD)** altamente optimizado capaz de reconocer dichas reglas sobre cualquier flujo de entrada.

### 1.2 Estructura de un Archivo de Especificación Flex (`.l`)
Todo archivo de especificación para Flex se divide estrictamente en **tres secciones**, separadas por el delimitador `%%`:

```flex
%{
  /* SECCIÓN 1: DEFINICIONES Y ENCABEZADOS EN C */
  #include <stdio.h>
  int contador_lineas = 1;
%}

/* Opciones de configuración y macros de expresiones regulares */
%option noyywrap
DIGITO [0-9]
LETRA  [a-zA-Z_]

%%

  /* SECCIÓN 2: REGLAS LÉXICAS Y ACCIONES EN C */
"if"         { printf("TOKEN_IF\n"); }
{DIGITO}+    { printf("TOKEN_NUMERO: %s\n", yytext); }
\n           { contador_lineas++; }
.            { printf("ERROR_LEXICO: %s\n", yytext); }

%%

  /* SECCIÓN 3: CÓDIGO DE USUARIO EN C (FUNCIÓN MAIN Y AUXILIARES) */
int main(int argc, char **argv) {
    yylex();
    return 0;
}
```

#### Explicación Detallada de las Secciones:
1. **Sección de Definiciones (Declaraciones y Macros):**
   * Todo código C envuelto entre `%{` y `%}` (header) se copia literalmente y en crudo a la parte superior de `lex.yy.c`. Aquí se incluyen librerías (`<stdio.h>`, `<stdlib.h>`), declaraciones de variables globales (como contadores de línea/columna) y prototipos de funciones.
   * Debajo del bloque `%{ ... %}`, se declaran las directivas o `macros` de alias de expresiones regulares (ej. `IDENTIFICADOR {LETRA}({LETRA}|{DIGITO})*`) y opciones como `%option noyywrap` (indica que el lexer no debe buscar más archivos al alcanzar el fin del archivo actual, `EOF`).
2. **Sección de Reglas Léxicas (Patrones y Acciones):**
   * Es el núcleo del archivo. Consiste en una lista de pares `patrón` y `{ acción en C }`.
   * **`yytext`**: Puntero a cadena de caracteres (`char*`) que almacena el **lexema exacto** que acaba de coincidir con el patrón.
   * **`yyleng`**: Variable entera (`int`) que almacena la **longitud en caracteres** del lexema actual en `yytext`.
   * **Precedencia y Resolución de Ambigüedades:** Flex aplica la regla de **la coincidencia más larga (Longest Match)**. Si dos o más reglas coinciden con la misma longitud de caracteres, Flex elige **la que fue escrita primero en el archivo `.l`**.
3. **Sección de Código de Usuario (`main` y `yylex`):**
   * Contiene el punto de entrada `main(int argc, char **argv)` de la aplicación C o las funciones auxiliares.
   * **`yylex()`**: Es la función central y autogenerada por Flex. Al invocar `yylex()`, el autómata comienza a leer caracteres del flujo apuntado por la variable de archivo **`yyin`** (por defecto, `stdin`) y ejecuta las acciones C correspondientes conforme reconoce los tokens, hasta llegar al fin de archivo.

---

## 2. Descripción del Lenguaje Diseñado: `MiniRust` (Subconjunto de Rust)

Para este proyecto, hemos definido **MiniRust**, un subconjunto estructural e imperativo del moderno lenguaje de sistemas **Rust**. Conserva su sintaxis estricta de tipos, palabras clave y declaraciones de funciones sin entrar en la complejidad del verificador de préstamos (*borrow checker*) o plantillas genéricas.

### 2.1 Especificación Gramatical y Léxica de MiniRust

| Categoría de Componente | Elementos Incluidos en MiniRust | Representación Token / Regex |
| :--- | :--- | :--- |
| **Palabras Clave (*Keywords*)** | `fn`, `let`, `mut`, `if`, `else`, `while`, `for`, `in`, `return`, `true`, `false` | Palabras exactas (ej. `TK_KEYWORD_FN`) |
| **Macros de Sistema** | `println!` | `TK_MACRO_PRINTLN` |
| **Tipos de Datos Primitivos** | `i32` (entero 32 bits), `f64` (flotante), `bool`, `char`, `String` | `TK_TYPE_I32`, `TK_TYPE_F64`, etc. |
| **Operadores Aritméticos** | `+`, `-`, `*`, `/`, `%` | `TK_OP_ADD`, `TK_OP_SUB`, etc. |
| **Operadores Relacionales** | `==`, `!=`, `<`, `>`, `<=`, `>=` | `TK_OP_EQ`, `TK_OP_LT`, etc. |
| **Operadores Lógicos y Asignación** | `&&`, `||`, `!`, `=`, `+=`, `-=` | `TK_OP_AND`, `TK_OP_ASSIGN`, etc. |
| **Delimitadores y Símbolos** | `(`, `)`, `{`, `}`, `[`, `]`, `:`, `;`, `,`, `.`, `->`, `..`, `&` | `TK_LPAREN`, `TK_LBRACE`, etc. |
| **Identificadores** | Nombres de variables y funciones | `[a-zA-Z_][a-zA-Z0-9_]*` |
| **Literales Numéricos** | Enteros y números decimales de punto flotante | `[0-9]+` y `[0-9]+\.[0-9]+` |
| **Literales de Cadena** | Cadenas delimitadas por comillas dobles con escape | `\"([^\"\\]|\\.)*\"` |
| **Comentarios** | Línea única (`//...`) y multilínea (`/* ... */`) | Ignorados sintácticamente (contados en posición) |

---

## 3. Documentación del Proceso de Creación e Instalación Paso a Paso

### 3.1 Proceso de Creación en Flex (`rust_lexer.l`)
1. **Mapeo del Alfabeto:** Redactamos `rust_lexer.l` colocando primero las palabras clave (`fn`, `let`, `mut`, `if`...) y símbolos largos (`==`, `->`, `+=`) **antes** de la regla general de identificadores (`[a-zA-Z_][a-zA-Z0-9_]*`). Esto garantiza que cuando el autómata lee la palabra `if`, la reconozca como `TK_KEYWORD_IF` y no como un identificador genérico.
2. **Control Geométrica de Posición (Línea y Columna):**
   Implementamos variables globales `line_num` y `col_num` en el bloque `%{ ... %}`. Cada coincidencia actualiza `col_num += yyleng`, mientras que los saltos de línea (`\n`) incrementan `line_num` y reinician `col_num = 1`.
3. **Manejo de Errores Léxicos (`.`):**
   Al final de todas las reglas, agregamos la regla comodín `.`. Si ningún patrón legítimo coincide con el carácter en la entrada (por ejemplo, los símbolos `@`, `$` o `¿` en MiniRust), se dispara esta regla lanzando una advertencia crítica en pantalla:
   `[!] ERROR LÉXICO CRÍTICO: Caracter no reconocido '¿' en Línea X, Columna Y`.

---

### 3.2 Guía de Instalación y Compilación del Analizador (`Flex` y `GCC`)

#### A. En Linux / Debian / Ubuntu / macOS (y terminal WSL en Windows)
1. **Instalar el metacompilador Flex y el compilador GCC:**
   ```bash
   sudo apt update
   sudo apt install flex gcc build-essential -y
   ```
2. **Generar el autómata en C (`lex.yy.c`) a partir del archivo de especificación (`rust_lexer.l`):**
   ```bash
   flex rust_lexer.l
   ```
   *(Este comando genera instantáneamente el archivo `lex.yy.c` en el directorio).*
3. **Compilar el código autogenerado con GCC:**
   ```bash
   gcc lex.yy.c -o analizador_rust
   ```
4. **Ejecutar el analizador sobre un programa de prueba:**
   ```bash
   ./analizador_rust ejemplo_rust1.rs
   ```

#### B. En Windows (Entorno Nativo / CMD / PowerShell sin Flex instalado)
Si en tu equipo Windows no tienes instaladas las herramientas GNU de C (`flex` y `gcc`), hemos provisto dos alternativas inmediatas dentro de la carpeta:
1. **Opción 1: Ejecutar el Emulador Equivalente en Python (`rust_lexer_py.py`):**
   Puedes verificar y demostrar la misma tokenización exacta sobre los archivos `.rs` utilizando Python en la consola:
   ```cmd
   python rust_lexer_py.py ejemplo_rust1.rs
   python rust_lexer_py.py ejemplo_rust2_errores.rs
   ```
2. **Opción 2: Instalar las Herramientas Flex/GCC en Windows (vía MSYS2 / MinGW):**
   * Descarga e instala **MSYS2** desde [msys2.org](https://www.msys2.org/).
   * En la terminal MSYS2 UCRT64, ejecuta:
     ```bash
     pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-flex
     ```
   * Agrega `C:\msys64\ucrt64\bin` a la variable de entorno `PATH` de Windows, y podrás compilar normalmente con `flex rust_lexer.l` y `gcc lex.yy.c -o analizador_rust.exe`.
