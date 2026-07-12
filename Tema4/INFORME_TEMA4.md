# INFORME TÉCNICO ACADÉMICO: TEMA 4 - ANÁLISIS LÉXICO
## UNIVERSIDAD NACIONAL EXPERIMENTAL DE GUAYANA (UNEG)
### VICERRECTORADO ACADÉMICO
### COORDINACIÓN GENERAL DE PREGRADO
#### LENGUAJES Y COMPILADORES (SECCIÓN 01)

---

* **Profesor:** Msc. Félix Márquez (`fmarquez@e.uneg.edu.ve`)
* **Integrantes del Equipo:**
  * Fernando Centeno
  * Juan Longart
  * Adrian Reina
  * Rafael Rodriguez
* **Ciudad Guayana, Julio de 2026**
* **Período Lectivo:** 2026-I
* **Evaluación:** Informe (15 ptos) + Defensa (10 ptos) = 25 ptos

---

## TABLA DE CONTENIDOS

1. [Introducción y Síntesis de la Unidad](#1-introducción-y-síntesis-de-la-unidad)
2. [Actividad 1: Autómatas de Pila (Definición, Ejemplos y Poder Computacional)](#2-actividad-1-autómatas-de-pila-pda)
3. [Actividad 2: Analizador Léxico para Archivos Docker desde Cero (`Python`)](#3-actividad-2-analizador-léxico-para-archivos-docker-python)
4. [Actividad 3: Subconjunto de Lenguaje Rust (`MiniRust`) usando Metacompilador `Flex`](#4-actividad-3-subconjunto-de-lenguaje-rust-minirust-con-flex)
5. [Actividad 4: Indagación de Flex en el Área de Seguridad Informática](#5-actividad-4-flex-en-el-área-de-seguridad-informática)
6. [Conclusiones Generales](#6-conclusiones-generales)
7. [Referencias Bibliográficas y Web](#7-referencias-bibliográficas-y-web)

---

## 1. INTRODUCCIÓN Y SÍNTESIS DE LA UNIDAD

El análisis léxico representa la primera fase y el punto de entrada fundamental dentro de la arquitectura de un compilador moderno. En esta etapa, el código fuente —concebido inicialmente por el computador como una secuencia continua y desestructurada de caracteres (bytes)— es leído, verificado y agrupado en unidades lógicas con significado semántico denominadas **componentes léxicos** o **tokens**. A este proceso se le conoce como **tokenización**.

El desarrollo del analizador léxico (*Lexer* o *Scanner*) se sustenta directamente en la teoría de máquinas abstractas impartida en las unidades previas: específicamente los **Autómatas Finitos Determinísticos (AFD)** y **No Determinísticos (AFND)**, los cuales reconocen los **Lenguajes Regulares (Chomsky Tipo 3)** definidos mediante **Expresiones Regulares (regex)**.

Para materializar esta fase, la ingeniería de compiladores ofrece dos grandes enfoques o metodologías de desarrollo que se exploran en este informe:
1. **Implementación Manual ("Desde Cero"):** Consiste en construir directamente el motor de lectura e iteración en un lenguaje general (como Python o C), aplicando expresiones regulares o implementando explícitamente la tabla de transiciones de estados del AFD en bucles condicionales. Brinda un control absoluto sobre el manejo de errores y rendimiento granular.
2. **Implementación mediante Metacompiladores (`Flex`):** Consiste en emplear herramientas generadoras especializadas que reciben como entrada un archivo de especificación declarativa (patrones y acciones C) y compilan automáticamente el código fuente en C del autómata determinístico subyacente (`lex.yy.c`), acelerando el ciclo de desarrollo y minimizando errores en gramáticas extensas.

---

## 2. ACTIVIDAD 1: AUTÓMATAS DE PILA (PDA)

### 2.1 Definición Formal
Un **Autómata de Pila** (*Pushdown Automaton* o **PDA**) es un modelo matemático de computación que extiende un Autómata Finito mediante la adición de una **memoria externa de acceso LIFO** (*Last-In, First-Out* o *pila*). Esta memoria infinita le permite almacenar símbolos intermedios para realizar conteos, verificaciones de balanceo y recordar dependencias pasadas, facultándolo para reconocer **Lenguajes Libres de Contexto (Chomsky Tipo 2)**.

Formalmente, un Autómata de Pila es una tupla de 7 componentes:
$$M = (Q, \Sigma, \Gamma, \delta, q_0, Z_0, F)$$

Donde:
* **$Q$**: Conjunto finito de estados del control finto.
* **$\Sigma$**: Alfabeto finito de entrada (símbolos leídos de la cadena).
* **$\Gamma$**: Alfabeto finito de la pila (símbolos que pueden apilarse/desapilarse).
* **$\delta$**: Función de transición: $\delta: Q \times (\Sigma \cup \{\epsilon\}) \times \Gamma \rightarrow \mathcal{P}(Q \times \Gamma^*)$.
* **$q_0$**: Estado inicial ($q_0 \in Q$).
* **$Z_0$**: Símbolo inicial en el fondo de la pila ($Z_0 \in \Gamma$).
* **$F$**: Conjunto de estados de aceptación ($F \subseteq Q$).

---

### 2.2 Ejemplos Prácticos de Autómatas de Pila

#### Ejemplo 1: Reconocedor de Cadenas Balanceadas $L_1 = \{a^n b^n \mid n \ge 1\}$
Este lenguaje no puede ser reconocido por ningún AFD (por el Lema del Bombeo regular), pero el Autómata de Pila lo resuelve apilando cada `$a$` que lee en la primera etapa y desapilando una `$a$` por cada `$b$` leída en la segunda etapa:

* **Especificación:** $Q = \{q_0, q_1, q_2\}$, $\Sigma = \{a, b\}$, $\Gamma = \{A, Z_0\}$, $F = \{q_2\}$.
* **Transiciones $\delta$:**
  1. $\delta(q_0, a, Z_0) = \{(q_0, AZ_0)\}$ *(apilar la primera a)*
  2. $\delta(q_0, a, A) = \{(q_0, AA)\}$ *(apilar as adicionales)*
  3. $\delta(q_0, b, A) = \{(q_1, \epsilon)\}$ *(al llegar la primera b, pasar a $q_1$ y desapilar)*
  4. $\delta(q_1, b, A) = \{(q_1, \epsilon)\}$ *(por cada b adicional, desapilar A)*
  5. $\delta(q_1, \epsilon, Z_0) = \{(q_2, Z_0)\}$ *(si la pila muestra $Z_0$ al terminar, aceptar en $q_2$)*

---

### 2.3 Utilidades y Poder Computacional (Comparación Chomsky)

| Criterio | Autómata Finito (AFD / AFND) | Autómata de Pila (PDA) |
| :--- | :--- | :--- |
| **Jerarquía de Chomsky** | **Tipo 3: Lenguajes Regulares** | **Tipo 2: Lenguajes Libres de Contexto (GLC)** |
| **Estructura de Memoria** | Finita fija (solo los estados $Q$). | Infinita estructurada (Estados + Pila LIFO). |
| **Capacidad de Conteo** | Nula (no puede verificar anidamientos infinitos). | Capaz de verificar paréntesis anidados, bloques `{}` y emparejamientos exactos. |
| **Aplicación en Compiladores** | **Analizador Léxico (`Lexer`)** | **Analizador Sintáctico (`Parser` LR / LL / YACC)** |

---

## 3. ACTIVIDAD 2: ANALIZADOR LÉXICO PARA ARCHIVOS DOCKER (`PYTHON`)

Para la segunda actividad, se implementó desde cero el módulo `dockerfile_lexer.py` utilizando expresiones regulares avanzadas en Python.

> [!IMPORTANT]
> **Aclaratoria Técnica:** La ejecución de este analizador léxico **no requiere tener instalado o ejecutándose el motor de Docker** en la computadora. El programa procesa el código fuente de los archivos `Dockerfile` en formato de texto plano para validar su gramática y emitir los tokens correspondientes.

### 3.1 Alfabeto y Patrones Léxicos del Dockerfile
* **Directivas (`DIRECTIVE`):** `FROM`, `RUN`, `CMD`, `LABEL`, `EXPOSE`, `ENV`, `ADD`, `COPY`, `ENTRYPOINT`, `VOLUME`, `USER`, `WORKDIR`, `ARG`, `HEALTHCHECK`, `SHELL`.
* **Flags (`FLAG`):** `--platform=...`, `--from=...`, `--chown=...`, `--interval=...`.
* **Variables (`VARIABLE`):** `$VAR` o `${VAR:-default}`.
* **Cadenas, Puertos y Palabras:** Cadenas entre comillas (`STRING`), puertos de red (`PORT`, ej. `8080/tcp`), enteros (`NUMBER`) e identificadores generales/rutas (`WORD`).

### 3.2 Evidencia de Pruebas y Reporte de Errores Léxicos
Al ejecutar `run_dockerfile_lexer.py`, el analizador evalúa los 3 ejemplos provistos:
1. **`Dockerfile_ejemplo1`:** Imagen de Node.js verificada exitosamente (`ACEPTADO - 36 tokens reconocidos`).
2. **`Dockerfile_ejemplo2`:** Multi-stage build con directivas avanzadas (`ACEPTADO - 65 tokens reconocidos`).
3. **`Dockerfile_ejemplo3_errores`:** Al encontrar un símbolo ilegal (`¿`), el lexer detiene el procesamiento e informa el error léxico con la posición exacta:
   ```text
   [!] ERROR LÉXICO en línea 7, columna 28:
       Carácter o secuencia no reconocida: '¿'
       Línea completa: >> RUN pip install -r requirements.txt ¿¿error_aqui?? ¡símbolos_inválidos! <<
   --- ESTADO: RECHAZADO (Se encontraron errores léxicos) ---
   ```

---

## 4. ACTIVIDAD 3: SUBCONJUNTO DE LENGUAJE RUST (`MINIRUST`) CON `FLEX`

### 4.1 Descripción del Lenguaje Diseñado (`MiniRust`)
`MiniRust` es un subconjunto estructurado y fuertemente tipado del lenguaje de programación **Rust**, diseñado para ilustrar la tokenización de un lenguaje de sistemas moderno.
* **Tipos soportados:** `i32`, `f64`, `bool`, `char`, `String`.
* **Palabras reservadas:** `fn`, `let`, `mut`, `if`, `else`, `while`, `for`, `in`, `return`, `true`, `false`, y la macro `println!`.
* **Operadores compuestos:** `==`, `!=`, `<=`, `>=`, `&&`, `||`, `->`, `..`, `+=`, `-=`.

### 4.2 Arquitectura del Especificador Flex (`rust_lexer.l`)
El archivo `.l` utiliza variables globales en C (`line_num` y `col_num`) combinadas con la macro `%option yylineno` para reportar con precisión milimétrica la fila y columna donde aparece cada lexema.

### 4.3 Manual de Instalación y Ejecución de Flex
* **En Linux / WSL:**
  ```bash
  flex rust_lexer.l
  gcc lex.yy.c -o analizador_rust
  ./analizador_rust ejemplo_rust1.rs
  ```
* **En Windows (Sin GCC/Flex instalado):**
  Se provee en la misma carpeta el módulo `rust_lexer_py.py`, el cual emula con exactitud la tabla de símbolos de Flex sobre el código MiniRust ejecutando: `python rust_lexer_py.py ejemplo_rust1.rs`.

---

## 5. ACTIVIDAD 4: FLEX EN EL ÁREA DE SEGURIDAD INFORMÁTICA

### 5.1 Indagación y Reflexión
En la ciberseguridad, la velocidad de inspección del tráfico y la validación de firmas de malware marcan la diferencia en la mitigación de ataques zero-day. Los analizadores léxicos generados por herramientas como **Flex** son fundamentales en los siguientes sistemas industriales:

1. **Motores IDS/IPS (Snort y Suricata):**
   Para detectar ataques en redes que operan a 10 Gbps o 100 Gbps, los motores de detección de intrusos tokenizan las cabeceras de red (`TCP/UDP/IP/ICMP`) y las reglas de inspección mediante autómatas determinísticos en C. Flex permite leer cada byte del flujo a velocidad lineal $O(n)$, sin retrocesos ni costosos bucles interpretados.
2. **Motores de Caza de Malware (Reglas YARA):**
   YARA, considerado la herramienta principal en análisis de malware forense, utiliza internamente **Flex y Bison** en su código fuente (`libyara`) para compilar los scripts de reglas de los analistas en un autómata en memoria antes de escanear binarios o volcados de memoria RAM.
3. **Firewalls de Aplicación Web (WAF - ModSecurity):**
   Tokenizan las peticiones HTTP (cabeceras, cookies, cuerpos URL-encoded o JSON) para detectar patrones léxicos de inyección SQL (`SQLi`), Cross-Site Scripting (`XSS`) o Path Traversal (`/../../etc/passwd`) antes de que lleguen al servidor web.

### 5.2 Demostración Práctica
En la carpeta `actividad4_seguridad_informatica/` se ha desarrollado y adjuntado la especificación `yara_lexer_demo.l`, la cual implementa un autómata Flex en C capaz de tokenizar secciones de firmas YARA (`rule`, `meta:`, `strings:`, `condition:`), modificadores (`ascii`, `wide`, `nocase`), variables de cadena (`$firma`) y firmas hexadecimales de malware (`{ E8 ?? ?? 8B 45 }`).

---

## 6. CONCLUSIONES GENERALES

1. La fase de **Análisis Léxico** es indispensable para simplificar el trabajo de los analizadores sintácticos y semánticos, al purificar el código fuente eliminando comentarios innecesarios, saltos de línea superfluos y validando la pertenencia de los caracteres al alfabeto del lenguaje.
2. Mientras que los **Autómatas Finitos (AFD)** dominan el análisis léxico gracias a su velocidad lineal y bajo consumo de memoria para tokens individuales, los **Autómatas de Pila (PDA)** asumen el liderazgo en el análisis sintáctico gracias a su memoria LIFO, permitiendo el balanceo de bloques y estructuras recursivas libres de contexto.
3. La elección entre desarrollar un analizador léxico **manual desde cero** (como se demostró en Python para Dockerfile) o utilizar un **metacompilador** (como se demostró en Flex para MiniRust) depende del contexto del proyecto: el enfoque manual ofrece personalización extrema en los mensajes de error, mientras que herramientas como Flex garantizan robustez, estandarización y máximo rendimiento industrial en lenguajes complejos y motores de seguridad cibernética.

---

## 7. REFERENCIAS BIBLIOGRÁFICAS Y WEB

1. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2007). *Compiladores: Principios, técnicas y herramientas (El Libro del Dragón)*. 2da Edición. Pearson Educación.
2. Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). *Introducción a la teoría de autómatas, lenguajes y computación*. 3ra Edición. Addison-Wesley.
3. Levine, J. (2009). *Flex & Bison: Text Processing Tools*. O'Reilly Media.
4. Documentación Oficial del Proyecto YARA: *The pattern matching swiss knife for malware researchers*. [https://virustotal.github.io/yara/](https://virustotal.github.io/yara/)
5. Documentación y Especificación del Lenguaje Rust: [https://doc.rust-lang.org/reference/](https://doc.rust-lang.org/reference/)
6. Márquez, F. (2026). *Guía de Estudio: Tema 4 (Análisis Léxico)*. Universidad Nacional Experimental de Guayana (UNEG).
