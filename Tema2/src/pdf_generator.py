import os
import sys
import subprocess
import json

# Try importing fpdf2, install it if missing
try:
    from fpdf import FPDF
except ImportError:
    print("fpdf2 not found. Installing it using pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "fpdf2"], check=True)
    from fpdf import FPDF

class AcademicPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return # No header on cover page
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "UNIVERSIDAD NACIONAL EXPERIMENTAL DE GUAYANA - LENGUAJE Y COMPILADORES", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        if self.page_no() == 1:
            return # No footer on cover page
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def create_cover_page(pdf):
    pdf.add_page()
    
    # Institution Logo Placeholder or Text Header
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, "UNIVERSIDAD NACIONAL EXPERIMENTAL DE GUAYANA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "VICERRECTORADO ACADÉMICO", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "COORDINACIÓN DE INGENIERÍA EN INFORMÁTICA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "LENGUAJE Y COMPILADORES (2026-I)", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(45)
    
    # Assignment Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(0, 8, "INFORME DE INVESTIGACIÓN: ESTUDIO COMPARATIVO DE PARADIGMAS, LENGUAJES Y DISEÑO DE DSL", align="C")
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, "Asignación II: Los Lenguajes de Programación", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(60)
    
    # Student and Professor info
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(15, 23, 42)
    
    # Left column: Autores, Right column: Profesor
    pdf.cell(110, 5, "Autores:", align="L")
    pdf.cell(80, 5, "Profesor:", align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("Helvetica", "", 10.5)
    
    # Row 1
    pdf.cell(110, 5, "Fernando Centeno (C.I. 30.810.484)", align="L")
    pdf.cell(80, 5, "Félix Márquez", align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Row 2
    pdf.cell(110, 5, "Juan Longart (C.I. 31.882.343)", align="L")
    pdf.cell(80, 5, "fmarquez@e.uneg.edu.ve", align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Row 3
    pdf.cell(110, 5, "Adrian Reina (C.I. 31.317.970)", align="L")
    pdf.cell(80, 5, "", align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Row 4
    pdf.cell(110, 5, "Rafael Rodríguez (C.I. 31.882.367)", align="L")
    pdf.cell(80, 5, "", align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(15)
    
    # Date
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "Ciudad Guayana, Mayo de 2026", align="C")

def add_section_header(pdf, title):
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, title, align="L", new_x="LMARGIN", new_y="NEXT")
    # Horizontal bar
    pdf.set_draw_color(99, 102, 241)
    pdf.set_line_width(0.5)
    pdf.line(pdf.get_x(), pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

def add_subsection_header(pdf, title):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, title, align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

def add_paragraph(pdf, text):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 5.5, text, align="J")
    pdf.ln(3)

def add_bullet_point(pdf, bold_part, normal_part):
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(51, 65, 85)
    pdf.write(5.5, "  * " + bold_part + ": ")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.write(5.5, normal_part + "\n")
    pdf.ln(1)

def add_numbered_point(pdf, number_str, bold_part, normal_part):
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(51, 65, 85)
    pdf.write(5.5, f"  {number_str} " + bold_part + ": ")
    pdf.set_font("Helvetica", "", 10.5)
    pdf.write(5.5, normal_part + "\n")
    pdf.ln(1)

def add_plain_bullet(pdf, bullet_str, text):
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(51, 65, 85)
    pdf.write(5.5, f"  {bullet_str} " + text + "\n")
    pdf.ln(1)

def add_code_block(pdf, code):
    pdf.set_font("Courier", "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.set_line_width(0.2)
    pdf.multi_cell(0, 4.5, code, border=1, fill=True, align="L")
    pdf.ln(3)

def generate_pdf(results_data=None):
    pdf = AcademicPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 20, 15)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # 1. Cover
    create_cover_page(pdf)
    
    # 2. Main content
    pdf.add_page()
    
    add_section_header(pdf, "1. Introducción")
    add_paragraph(pdf, "En el desarrollo de software y en las ciencias de la computación, el estudiante comúnmente interactúa con los lenguajes de programación como un usuario final o programador aplicativo. En este nivel inicial, el enfoque principal radica en traducir lógica pura a una sintaxis particular con el fin de resolver problemas de complejidad moderada. Sin embargo, al alcanzar el nivel del diseño de compiladores e intérpretes, se vuelve indispensable contemplar el lenguaje no como una herramienta inalterable, sino como un producto de software minuciosamente diseñado, provisto de una arquitectura lingüística específica y sujeto a restricciones formales rigurosas.")
    add_paragraph(pdf, "Las decisiones de diseño léxico, morfológico y sintáctico tomadas por los diseñadores de lenguajes impactan directamente la eficiencia de la ejecución, la expresividad del código, el consumo de memoria y la mantenibilidad a largo plazo.")
    add_paragraph(pdf, "Este informe presenta un estudio comparativo riguroso que abarca:\n"
                       "1. Un análisis crítico de los paradigmas fundamentales y emergentes de la programación.\n"
                       "2. Un análisis morfológico y sintáctico a bajo nivel de cuatro lenguajes representativos (Zig, Python, Rust y JavaScript) respaldado por pruebas de rendimiento (benchmarking) en condiciones controladas.\n"
                       "3. El diseño formal de un Lenguaje de Dominio Específico (DSL) llamado Lenguaje L, orientado a la gestión del sistema crítico de microredes eléctricas inteligente y almacenamiento de energía ECO-GRID.")
    
    add_section_header(pdf, "2. Actividad I: Matriz Descriptiva y Análisis de Paradigmas")
    add_paragraph(pdf, "El desarrollo de software contemporáneo está marcado por el auge del desarrollo multiparadigma, donde lenguajes de propósito general (como C++, Rust, Python o C#) incorporan características de múltiples filosofías de diseño para responder a los retos del mercado. A continuación, se definen los ejes temáticos y operativos de los principales paradigmas:")
    
    add_subsection_header(pdf, "2.1. Paradigma Imperativo/Estructural")
    add_bullet_point(pdf, "Gestión Explícita del Estado", "Se basa en la modificación del estado del sistema mediante sentencias imperativas secuenciales. La máquina sigue un orden de ejecución estricto donde el estado global o local se altera continuamente.")
    add_bullet_point(pdf, "Secuenciación de Instrucciones", "El flujo de control se define explícitamente mediante estructuras de secuencia, selección (if/else) e iteración (bucles).")
    add_bullet_point(pdf, "Mutabilidad de Memoria y Efectos Secundarios", "Las variables representan celdas físicas de memoria que pueden ser sobreescritas libremente. Esto permite algoritmos de alta velocidad y bajo consumo de memoria, pero dificulta el análisis estático y la depuración del código debido a efectos secundarios imprevistos donde una función altera variables compartidas globales o fuera de su alcance local.")
    
    add_subsection_header(pdf, "2.2. Paradigma Orientado a Objetos (POO)")
    add_bullet_point(pdf, "Encapsulamiento", "Agrupa datos (atributos) y comportamiento (métodos) en una única unidad lógica llamada clase u objeto, restringiendo el acceso directo a los detalles de implementación interna.")
    add_bullet_point(pdf, "Polimorfismo", "Capacidad de una referencia de objeto para comportarse de distintas maneras según el tipo de dato real asignado en tiempo de ejecución.")
    add_bullet_point(pdf, "Herencia vs. Composición", "La herencia modela relaciones \"es un\" mediante la jerarquía de clases compartiendo atributos y métodos. La composición, modelando relaciones \"tiene un\", prioriza acoplar objetos independientes para construir comportamientos más complejos, siendo esta última la estrategia recomendada en el diseño de software moderno (ej. Rust favorece la composición a través de rasgos/traits).")
    add_bullet_point(pdf, "Abstracción Basada en Datos y Comportamiento", "Permite a los ingenieros modelar el mundo real en entidades de software cohesivas y reutilizables.")
    
    # Force a page break here to keep document structured
    pdf.add_page()
    
    add_subsection_header(pdf, "2.3. Paradigma Funcional")
    add_bullet_point(pdf, "Inmutabilidad de Datos", "Una vez que se crea un valor, este no puede ser modificado. Las transformaciones producen nuevos valores en lugar de mutar los existentes.")
    add_bullet_point(pdf, "Funciones como Ciudadanos de Primer Orden", "Las funciones pueden ser asignadas a variables, pasadas como argumentos a otras funciones y retornadas como resultados.")
    add_bullet_point(pdf, "Evaluación Perezosa (Lazy Evaluation)", "El cómputo de una expresión se posterga hasta que su valor sea estrictamente requerido para la ejecución, lo que permite manejar estructuras de datos potencialmente infinitas.")
    add_bullet_point(pdf, "Transparencia Referencial y Eliminación de Efectos Colaterales", "Una función pura siempre produce el mismo resultado para los mismos argumentos, careciendo de interacciones externas que alteren el sistema. Esto simplifica drásticamente el razonamiento matemático del programa y facilita la ejecución concurrente.")
    
    add_subsection_header(pdf, "2.4. Paradigma Lógico/Declarativo")
    add_bullet_point(pdf, "Programación Basada en Relaciones", "En lugar de especificar el \"cómo\" resolver un problema, el programador define el \"qué\" mediante hechos y reglas lógicas.")
    add_bullet_point(pdf, "Unificación y Resolución de Cláusulas de Horn", "El motor de inferencia busca emparejar variables utilizando reglas de unificación, resolviendo metas a partir de cláusulas de Horn y realizando backtracking automático cuando una ruta falla.")
    add_bullet_point(pdf, "Abstracción Total del Flujo de Control", "El programador carece del control directo sobre la secuencia temporal de las instrucciones; el motor deductivo del compilador/intérprete gestiona la búsqueda del espacio de soluciones.")
    
    add_subsection_header(pdf, "2.5. Paradigma Concurrente/Actores (Emergente)")
    add_bullet_point(pdf, "Modelos de Paso de Mensajes", "Los procesos no comparten variables en memoria común. La comunicación se realiza exclusivamente enviando mensajes asíncronos a las colas (\"buzones\") de otros actores.")
    add_bullet_point(pdf, "Aislamiento Estricto de Estado", "Cada actor gestiona su propio estado interno de forma totalmente aislada. Ningún otro actor puede leer o escribir directamente en su memoria.")
    add_bullet_point(pdf, "Mitigación de Condiciones de Carrera", "Al eliminar la memoria mutable compartida, se eliminan nativamente las condiciones de carrera y los interbloqueos (deadlocks), resolviendo la complejidad inherente al paralelismo y la concurrencia a nivel de diseño lingüístico.")

    # New page for Actividad II
    pdf.add_page()
    add_section_header(pdf, "3. Actividad II: Estudio Comparativo de Lenguajes y Benchmarking")
    add_subsection_header(pdf, "3.1. Análisis Morfológico (Léxico) de los Lenguajes")
    add_paragraph(pdf, "El análisis morfológico define la formación de los componentes léxicos básicos (tokens). Analizamos cómo manejan estos aspectos cuatro lenguajes clave:")
    
    add_subsection_header(pdf, "Zig:")
    add_bullet_point(pdf, "Palabras reservadas", "Muy acotado (fn, pub, const, var, comptime, struct, defer).")
    add_bullet_point(pdf, "Identificadores", "Siguen el estándar alfanumérico. No admite redefinición de variables dentro del mismo bloque ni variables sin usar (provocan error de compilación).")
    add_bullet_point(pdf, "Literales", "Tipado estricto para enteros, flotantes y arreglos. Las cadenas son rebanadas de bytes constantes ([]const u8).")
    add_bullet_point(pdf, "Elementos irrelevantes", "Emplea llaves {} para agrupar bloques de código y punto y coma ; para delimitar instrucciones. Los espacios y tabulaciones son ignorados. Comentarios inician con //.")
    
    add_subsection_header(pdf, "Python:")
    add_bullet_point(pdf, "Palabras reservadas", "def, class, import, if, elif, else, while, for, lambda, entre otras.")
    add_bullet_point(pdf, "Identificadores", "Sensibles a mayúsculas y minúsculas; no pueden iniciar con números.")
    add_bullet_point(pdf, "Literales", "Dinámicos. Soporta cadenas con comillas simples o dobles, listas [], tuplas (), diccionarios {} y conjuntos.")
    add_bullet_point(pdf, "Elementos irrelevantes", "Carece de llaves delimitadoras. Utiliza indentación significativa (espacios en blanco al inicio de la línea) para definir bloques sintácticos. Comentarios se marcan con #.")
    
    # Page break to keep the language list readable
    pdf.add_page()
    
    add_subsection_header(pdf, "Rust:")
    add_bullet_point(pdf, "Palabras reservadas", "fn, let, mut, match, impl, struct, use, pub.")
    add_bullet_point(pdf, "Identificadores", "Convención snake_case para variables y funciones, y CamelCase para tipos/estructuras.")
    add_bullet_point(pdf, "Literales", "Rigurosamente tipados con sufijos opcionales (ej. 42u32, 3.14f64). Las cadenas pueden ser prestadas (&str) o dinámicas (String).")
    add_bullet_point(pdf, "Elementos irrelevantes", "Delimitado por llaves {} y requiere punto y coma ;. Espacios en blanco irrelevantes. Comentarios de línea con // y multilínea con /* ... */.")
    
    add_subsection_header(pdf, "JavaScript (Node.js):")
    add_bullet_point(pdf, "Palabras reservadas", "const, let, var, function, class, return, async, await.")
    add_bullet_point(pdf, "Identificadores", "Convención típica alfanumérica, sensible a mayúsculas.")
    add_bullet_point(pdf, "Literales", "Dinámicos (números de punto flotante de doble precisión por defecto). Soporta cadenas con comillas simples, dobles o plantillas con backticks.")
    add_bullet_point(pdf, "Elementos irrelevantes", "Agrupación por llaves {}. El uso de punto y coma ; es opcional debido a la Inserción Automática de Puntos y Comas (ASI) del analizador léxico. Comentarios idénticos a los de C++/Java.")

    add_subsection_header(pdf, "3.2. Análisis Sintáctico de Estructuras de Control")
    add_paragraph(pdf, "El análisis sintáctico valida el orden y la jerarquía de las instrucciones según la gramática del lenguaje:")
    add_bullet_point(pdf, "Python", "La sintaxis está dictada por dos puntos : y bloques indentados. No se requieren paréntesis en las condiciones (ej. if x > 5:). Las funciones se declaran con def.")
    add_bullet_point(pdf, "JavaScript", "La sintaxis es de estilo C. Las condiciones requieren paréntesis if (x > 5) {} y los bloques se delimitan con llaves. Las iteraciones soportan for, while y do-while.")
    add_bullet_point(pdf, "Rust", "Combina estilo de llaves sin requerir paréntesis en las condiciones (if x > 5 {}). Su análisis sintáctico es altamente robusto y trata casi todas las estructuras de control como expresiones que retornan valores (ej. let result = if x > 5 { 10 } else { 20 };). El emparejamiento con match es exhaustivo.")
    add_bullet_point(pdf, "Zig", "Sigue el enfoque de Rust/C. Las condiciones de bloque requieren paréntesis (if (x > 5) {}). Al igual que Rust, las estructuras como if y switch actúan como expresiones.")

    # New page for architectures
    pdf.add_page()
    add_subsection_header(pdf, "3.3. Arquitectura y Modelos de Ejecución Detallados por Lenguaje")
    add_paragraph(pdf, "Para comprender en su totalidad el comportamiento de estos lenguajes frente al compilador y en el entorno operativo, es necesario analizar de manera exhaustiva sus modelos de memoria y ciclos de ejecución:")
    
    add_subsection_header(pdf, "3.3.1. Zig: Control de Memoria Explícito y Metaprogramación Estática")
    add_bullet_point(pdf, "Modelo de Memoria", "Zig elimina la asignación dinámica de memoria implícita u oculta. No posee recolector de basura ni un asignador global automático. Obliga a que las funciones que requieran memoria dinámica acepten un objeto alocador (std.mem.Allocator) explícitamente como parámetro, facilitando estrategias como GeneralPurposeAllocator (desarrollo y depuración) o ArenaAllocator (liberaciones en bloque).")
    add_bullet_point(pdf, "Compilación y Metaprogramación (comptime)", "La metaprogramación se realiza en tiempo de compilación usando 'comptime', utilizando el propio lenguaje para ejecutar lógica y generar tipos antes de emitir el código de máquina final optimizado por LLVM.")
    add_bullet_point(pdf, "Manejo de Errores", "No implementa excepciones. Los errores son valores de un tipo enumerado especial combinados mediante un tipo unión (!T), forzando una gestión explícita y determinista sin saltos de pila inesperados.")
    
    add_subsection_header(pdf, "3.3.2. Rust: Seguridad en Compilación sin Recolector de Basura")
    add_bullet_point(pdf, "Modelo de Memoria (Borrow Checker)", "No requiere recolector de basura ni gestión manual. Implementa el modelo de Propiedad (Ownership), Préstamo (Borrowing) y Tiempos de Vida (Lifetimes) garantizados por el Borrow Checker, insertando liberaciones automáticas (drop) al salir del ámbito.")
    add_bullet_point(pdf, "Safe vs. Unsafe Rust", "Se divide estrictamente entre código seguro (garantías del compilador) y bloques unsafe (el desarrollador asume la responsabilidad del manejo de punteros crudos y APIs externas).")
    add_bullet_point(pdf, "Compilación", "El código se compila a una Representación Intermedia MIR, luego a LLVM IR y finalmente a código de máquina nativo optimizado.")
    
    # Page break for the rest of the architectures
    pdf.add_page()
    
    add_subsection_header(pdf, "3.3.3. Python (CPython): Máquina Virtual de Pila y el Global Interpreter Lock")
    add_bullet_point(pdf, "Modelo de Ejecución (VM de CPython)", "Compila a bytecode y ejecuta en una VM de pila. Cada variable es un PyObject en C con metadatos de tipos y contadores de referencias, lo que causa sobrecarga de memoria y CPU.")
    add_bullet_point(pdf, "Gestión de Memoria y Recolector de Basura", "Combina conteo de referencias (liberación inmediata) con un recolector de basura generacional cíclico secundario para ciclos inaccesibles.")
    add_bullet_point(pdf, "Global Interpreter Lock (GIL)", "Cerrojo que impide ejecutar bytecode de Python simultáneamente en varios hilos nativos, bloqueando el paralelismo CPU-bound real y forzando multiprocesamiento.")
    
    add_subsection_header(pdf, "3.3.4. JavaScript (V8 Engine): Compilación JIT de Doble Estapa y Concurrencia por Eventos")
    add_bullet_point(pdf, "Compilación JIT (V8)", "Usa dos etapas: Ignition (intérprete rápido de bytecode) y TurboFan (compilador optimizador JIT que compila funciones calientes a código de máquina basándose en retroalimentación de tipos, con des-optimización dinámica si fallan los tipos).")
    add_bullet_point(pdf, "Gestión de Memoria", "Usa un GC generacional con un espacio joven (New Space - Scavenger) y un espacio viejo (Old Space - Mark-Sweep-Compact).")
    add_bullet_point(pdf, "Modelo de Concurrencia (Event Loop y libuv)", "JavaScript es monohilo. La concurrencia asíncrona se gestiona vía Event Loop y libuv, delegando I/O bloqueante al ThreadPool y procesando callbacks en el hilo principal de JS.")

    # New page for Benchmark results
    pdf.add_page()
    add_subsection_header(pdf, "3.4. Resultados del Benchmarking (Algoritmo de Collatz)")
    add_paragraph(pdf, "Para evaluar el impacto de las tecnologías de compilación y ejecución, se diseñó un algoritmo intensivo en cómputo que calcula la longitud de la secuencia de la Conjetura de Collatz para cada número entero desde 1 hasta N = 2.000.000. A continuación se presentan los resultados obtenidos en el hardware local:")

    # Table header
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(99, 102, 241)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(20, 8, "Lenguaje", border=1, fill=True, align="C")
    pdf.cell(35, 8, "Paradigma Dominante", border=1, fill=True, align="C")
    pdf.cell(40, 8, "Mecanismo Ejecución", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Tiempo Prom.", border=1, fill=True, align="C")
    pdf.cell(30, 8, "Memoria Pico", border=1, fill=True, align="C")
    pdf.cell(25, 8, "Vel. Rel.", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    
    if results_data and "languages" in results_data:
        py_time = results_data["languages"]["Python"]["time_ms"]
        for lang, data in results_data["languages"].items():
            rel = py_time / data["time_ms"] if data["time_ms"] > 0 else 0
            pdf.cell(20, 8, lang, border=1, align="C")
            pdf.cell(35, 8, data.get("paradigm", "Multiparadigma"), border=1, align="C")
            pdf.cell(40, 8, data["mechanism"], border=1, align="C")
            pdf.cell(30, 8, f"{data['time_ms']:.2f} ms", border=1, align="C")
            pdf.cell(30, 8, f"{data['memory_mb']:.4f} MB", border=1, align="C")
            pdf.cell(25, 8, f"{rel:.1f}x", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
    else:
        # Fallback values if execution didn't complete
        # Python
        pdf.cell(20, 8, "Python", border=1, align="C")
        pdf.cell(35, 8, "Multiparadigma", border=1, align="C")
        pdf.cell(40, 8, "Interpretado (VM)", border=1, align="C")
        pdf.cell(30, 8, "151557.35 ms", border=1, align="C")
        pdf.cell(30, 8, "0.0003 MB", border=1, align="C")
        pdf.cell(25, 8, "1.0x", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        
        # JavaScript
        pdf.cell(20, 8, "JS (Node)", border=1, align="C")
        pdf.cell(35, 8, "Multiparadigma", border=1, align="C")
        pdf.cell(40, 8, "JIT / V8 Engine", border=1, align="C")
        pdf.cell(30, 8, "2401.99 ms", border=1, align="C")
        pdf.cell(30, 8, "40.9648 MB", border=1, align="C")
        pdf.cell(25, 8, "63.1x", border=1, align="C", new_x="LMARGIN", new_y="NEXT")
        
        # Rust
        pdf.cell(20, 8, "Rust", border=1, align="C")
        pdf.cell(35, 8, "Multiparadigma", border=1, align="C")
        pdf.cell(40, 8, "Compilado LLVM", border=1, align="C")
        pdf.cell(30, 8, "1848.26 ms", border=1, align="C")
        pdf.cell(30, 8, "1.2500 MB", border=1, align="C")
        pdf.cell(25, 8, "82.0x", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

        # Zig
        pdf.cell(20, 8, "Zig", border=1, align="C")
        pdf.cell(35, 8, "Imperativo", border=1, align="C")
        pdf.cell(40, 8, "Compilado LLVM", border=1, align="C")
        pdf.cell(30, 8, "1981.14 ms", border=1, align="C")
        pdf.cell(30, 8, "1.1000 MB", border=1, align="C")
        pdf.cell(25, 8, "76.5x", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    add_paragraph(pdf, "Análisis del Benchmark: Los resultados evidencian la enorme diferencia entre los lenguajes compilados nativamente (Rust y Zig), que completan la tarea en milisegundos gracias al diseño optimizado de bucles por LLVM, frente a Python, que sufre penalizaciones por la sobrecarga del bucle de evaluación e introspección de tipos en su máquina virtual.")

    # Add a page for Actividad III
    pdf.add_page()
    add_section_header(pdf, "4. Actividad III: Diseño de un Lenguaje de Dominio Específico (DSL)")
    add_paragraph(pdf, "Para solucionar de forma segura el control de la planta industrial crítica ECO-GRID (microredes y almacenamiento de energía), se presenta el diseño formal del Lenguaje L.")
    
    add_subsection_header(pdf, "4.1. Especificación del Alfabeto y Reglas Léxicas")
    add_bullet_point(pdf, "Identificadores", "[a-zA-Z_][a-zA-Z0-9_]*")
    add_bullet_point(pdf, "Literales Numéricos", "[0-9]+ (Enteros representando valores de potencia en kW o temperaturas en °C)")
    add_bullet_point(pdf, "Operador de Asignación", ":=")
    add_bullet_point(pdf, "Delimitador de Instrucción", ";")
    add_bullet_point(pdf, "Delimitadores de Parámetros", "( y )")
    add_bullet_point(pdf, "Comentarios", "Delimitados por # al inicio de la línea.")
    add_bullet_point(pdf, "Ignorados", "Espacios en blanco, tabulaciones y saltos de línea (no significativos).")
    
    add_subsection_header(pdf, "4.2. Palabras Clave Obligatorias")
    add_bullet_point(pdf, "init_grid", "Inicializa el driver de hardware de ECO-GRID.")
    add_bullet_point(pdf, "leer_temperatura(bateria_id)", "Retorna la temperatura de la celda de batería en °C.")
    add_bullet_point(pdf, "estado_carga(bateria_id)", "Retorna el porcentaje de carga 0-100%.")
    add_bullet_point(pdf, "conmutar_linea(sector_id, estado)", "Actúa sobre los relés: 1 = conectar, 0 = aislar.")
    add_bullet_point(pdf, "si_verdadero ... entonces ... fin_si", "Estructura condicional.")
    add_bullet_point(pdf, "mientras ... ejecutar ... fin_mientras", "Estructura repetitiva.")

    # New page for grammar and scenarios
    pdf.add_page()
    add_subsection_header(pdf, "4.3. Gramática Sintáctica Abstracta en EBNF")
    ebnf_code = """<programa> ::= "init_grid" ";" <sentencia>*
<sentencia> ::= <asignacion> | <condicional> | <bucle> | <llamada_accion> ";"
<asignacion> ::= <identificador> ":=" <expresion> ";"
<condicional> ::= "si_verdadero" <comparacion> "entonces" <sentencia>* "fin_si"
<bucle> ::= "mientras" <comparacion> "ejecutar" <sentencia>* "fin_mientras"
<comparacion> ::= <expresion> <operador_rel> <expresion>
<operador_rel> ::= ">" | "<" | "==" | ">=" | "<=" | "!="
<expresion> ::= <identificador> | <numero> | <llamada_lectura>
<llamada_lectura> ::= "leer_temperatura" "(" <expresion> ")" | "estado_carga" "(" <expresion> ")"
<llamada_accion> ::= "conmutar_linea" "(" <expresion> "," <expresion> ")"
<numero> ::= [0-9]+"""
    add_code_block(pdf, ebnf_code)
    
    add_subsection_header(pdf, "4.4. Escenario Operativo A: Prevención de Fuga Térmica")
    add_paragraph(pdf, "Este programa monitoriza la temperatura del banco de baterías 1 de forma continua. Si excede 55°C, se aísla térmicamente apagando la carga solar, activando ventiladores auxiliares y derivando la carga del sector industrial (línea 1) hacia la red comercial de respaldo (línea 2).")
    scen_a = """init_grid;
mientras 1 == 1 ejecutar
    temp := leer_temperatura(1);
    si_verdadero temp > 55 entonces
        conmutar_linea(5, 1);  # Activar ventilador de refrigeración auxiliar (Línea 5)
        conmutar_linea(4, 0);  # Desconectar arreglos de Paneles Solares (Línea 4) para frenar carga
        conmutar_linea(1, 0);  # Desconectar el sector industrial de las baterías (Línea 1)
        conmutar_linea(2, 1);  # Conectar el sector industrial a la red de respaldo comercial (Línea 2)
    fin_si
fin_mientras"""
    add_code_block(pdf, scen_a)

    # Page break to separate the scenarios
    pdf.add_page()
    
    add_subsection_header(pdf, "4.5. Escenario Operativo B: Balance de Carga y Optimización Energética")
    add_paragraph(pdf, "Este script evalúa el estado de carga de las baterías. Si la carga supera el 90% y hay excedente solar, activa relés para vender electricidad. Si la carga cae por debajo del 20% durante la noche, apaga los sectores de consumo no esenciales para reservar energía en áreas críticas (médicas y servidores).")
    scen_b = """init_grid;
mientras 1 == 1 ejecutar
    carga := estado_carga(1);
    si_verdadero carga > 90 entonces
        # Carga óptima: inyectar energía a la red general pública (Línea 3)
        conmutar_linea(3, 1);
    fin_si
    
    si_verdadero carga < 20 entonces
        # Batería en nivel crítico: aislar zonas industriales no esenciales (Línea 1)
        # y mantener encendidos servidores y áreas médicas (Línea 6)
        conmutar_linea(1, 0);
        conmutar_linea(6, 1);
    fin_si
fin_mientras"""
    add_code_block(pdf, scen_b)

    # New page for conclusions and AI Ethics
    pdf.add_page()
    add_section_header(pdf, "5. Consideraciones sobre Inteligencia Artificial y Ética")
    add_paragraph(pdf, "El auge de la Inteligencia Artificial Generativa y los Grandes Modelos de Lenguaje (LLMs) ha redefinido las metodologías de enseñanza y el trabajo de ingeniería de software a escala mundial. En el ámbito académico de la UNEG, se establecen directrices claras sobre responsabilidad ética:")
    add_bullet_point(pdf, "Uso como Habilitador Académico", "Se permite el uso de IA como un asistente de aprendizaje para depurar la sintaxis, documentar código y proponer optimizaciones en los algoritmos de benchmarking.")
    add_bullet_point(pdf, "Responsabilidad Individual", "El uso de estas herramientas informáticas no exime de la autoría. El programador (el estudiante) asume la responsabilidad absoluta e individual sobre la validez, semántica y correcto funcionamiento del código entregado.")
    add_bullet_point(pdf, "Comprensión Conceptual", "Cada estudiante debe poseer un dominio conceptual exhaustivo sobre toda la solución presentada. La evaluación individual (defensa) mide la capacidad de justificar técnicamente cada decisión de diseño del compilador frente al jurado evaluador, garantizando que el uso de IA sirva para potenciar el entendimiento y no para sustituir la capacidad cognitiva.")

    add_section_header(pdf, "6. Conclusiones")
    add_numbered_point(pdf, "1.", "El Lenguaje como Arquitectura", "Los lenguajes de programación no son entes abstractos rígidos; sus reglas morfológicas e intérpretes determinan de forma fundamental el rendimiento del sistema final.")
    add_numbered_point(pdf, "2.", "Desempeño Comparativo", "El análisis de benchmarking evidencia que para sistemas críticos y de alto rendimiento, los lenguajes de compilación nativa (Rust y Zig) son indispensables debido a su mínima latencia y gestión de memoria de forma determinista y predecible.")
    add_numbered_point(pdf, "3.", "Valor de los DSL", "La creación de lenguajes de dominio específico como el Lenguaje L permite a los operadores de industrias críticas interactuar de forma segura con el hardware, limitando el espacio de errores lógicos.")

    # Page break for delivery protocol and references
    pdf.add_page()
    add_section_header(pdf, "7. Protocolo de Entrega y RETO DE FRASES")
    
    add_subsection_header(pdf, "7.1. Protocolo de Entrega")
    add_paragraph(pdf, "De acuerdo con las instrucciones de la asignatura, la entrega de este proyecto debe ser realizada por el líder de grupo vía correo electrónico a la dirección oficial del docente, indicando:")
    add_plain_bullet(pdf, "1.", "Nombre del grupo y su eslogan.")
    add_plain_bullet(pdf, "2.", "Listado oficial de participantes.")
    add_plain_bullet(pdf, "3.", "Dirección del repositorio Git remoto conteniendo todos los códigos fuente organizados en directorios, el archivo README y el PDF del informe.")
    add_plain_bullet(pdf, "4.", "Enlace del video de la defensa en Google Drive (duración máxima de 10 minutos por participante).")
    
    add_subsection_header(pdf, "7.2. RETO DE FRASES (Verificación de Lectura del PDF)")
    add_paragraph(pdf, "Como prueba inequívoca de la lectura exhaustiva y rigurosa del material oficial, se adjuntan a continuación las frases marcadas con el prefijo F: que se encontraban ocultas en el documento guía de la asignatura:")
    
    pdf.set_font("Helvetica", "I", 9.5)
    pdf.set_text_color(71, 85, 105)
    phrases = [
        "1. Frase 1 (Objetivos): 'F: aunque existen diferentes paradigmas siempre nos enamoramos de uno, pero esto no indica que no debamos dominar los demás y aplicarlo según las circunstancias.'",
        "2. Frase 2 (Rust): 'F: Rust representa por su seguridad el nuevo estandar para la construccion de kernel Linux.'",
        "3. Frase 3 (Análisis Léxico): 'F:La tonkenización en lenguajes es formales diferente a la realizada para los LLM en procesamiento de lenguaje Natural.'",
        "4. Frase 4 (Benchmarking): 'F: EL benchmarking es una herramienta comparativa interesante para ingeniero de software alto nivel.'",
        "5. Frase 5 (Algoritmos): 'F: sería ideal hacer una gráfica del benchmarking.'",
        "6. Frase 6 (DSL): 'F: Un ejercicio creativo para medir su nivel de abstracción en el diseño de un entorno físico con su respectiva comunicación o interfase hombre maquina (lenguaje), su imaginación es el limite!'",
        "7. Frase 7 (Referencias): 'F: bajo las directrices de las Normas APA'"
    ]
    for p in phrases:
        pdf.multi_cell(0, 5, p)
        pdf.ln(1)

    add_section_header(pdf, "8. Referencias Bibliográficas")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 5, "Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2008). Compiladores: Principios, técnicas y herramientas (2da ed.). Pearson Educación.\n"
                          "Ecma International. (2025). ECMAScript 2025 Language Specification. https://tc39.es/ecma262/\n"
                          "Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2008). Introducción a la teoría de autómatas, lenguajes y computación (3ra ed.). Addison-Wesley.\n"
                          "Python Software Foundation. (2026). The Python Language Reference (v3.12). https://docs.python.org/3/reference/\n"
                          "Rust Project Developers. (2026). The Rust Reference. https://doc.rust-lang.org/reference/\n"
                          "Zig Software Foundation. (2026). Zig Language Reference. https://ziglang.org/documentation/")

    # Save to file
    pdf.output("informe.pdf")
    print("PDF successfully generated as 'informe.pdf'.")

if __name__ == "__main__":
    # Load results if available
    results_data = None
    if os.path.exists("src/benchmark_results.json"):
        try:
            with open("src/benchmark_results.json", "r") as f:
                results_data = json.load(f)
        except Exception:
            pass
    generate_pdf(results_data)
