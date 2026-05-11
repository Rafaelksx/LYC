"""Generador del informe PDF - Mecanismos WASM y APIs."""
import os
from fpdf import FPDF
from contenido import SECCIONES, REFERENCIAS

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uneg-logo.png")

class InformeWASM(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.cell(0, 10, "Mecanismos WASM y su importancia en APIs", align="C")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

    def portada(self):
        self.add_page()
        # Logo UNEG centrado (más compacto)
        logo_w = 30
        x_logo = (self.w - logo_w) / 2
        self.image(LOGO_PATH, x=x_logo, y=12, w=logo_w)
        self.ln(35)
        # Universidad - SIN negrita
        self.set_font("Helvetica", "", 13)
        self.cell(0, 8, "UNIVERSIDAD NACIONAL EXPERIMENTAL DE GUAYANA", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 11)
        self.cell(0, 7, "Vicerrectorado Académico", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 7, "Coordinación General de Pregrado", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 7, "Ingeniería en Informática", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 7, "Lenguajes y Compiladores", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(15)
        # Título del tópico
        self.set_font("Helvetica", "B", 15)
        self.multi_cell(0, 9, "MECANISMOS QUE INTERACTÚAN EN WASM\nY SU IMPORTANCIA EN TIEMPO DE\nRESPUESTA DE LAS API", align="C")
        self.ln(8)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, "Tópico 15", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        # Grupo y eslogan
        self.set_font("Helvetica", "", 10)
        self.cell(0, 7, "Grupo: Compiladores CLRR", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 7, "Eslogan: Los que mas compilan", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        # Profesor a la IZQUIERDA e Integrantes a la DERECHA
        col_w = (self.w - 50) / 2  # ancho de cada columna
        y_start = self.get_y()
        # Columna izquierda: Profesor
        self.set_font("Helvetica", "B", 10)
        self.cell(col_w, 7, "Profesor:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.cell(col_w, 6, "Félix Márquez", new_x="LMARGIN", new_y="NEXT")
        y_after_prof = self.get_y()
        # Columna derecha: Integrantes
        self.set_y(y_start)
        self.set_x(25 + col_w + 10)
        self.set_font("Helvetica", "B", 10)
        self.cell(col_w, 7, "Integrantes:", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        integrantes = [
            "Rafael Rodriguez - C.I.: 31882367 - Sec. 1",
            "Adrian Reina - C.I.: 31317970 - Sec. 1",
            "Fernando Centeno - C.I.: 31810484 - Sec. 1",
            "Juan Longart - C.I.: 31882343 - Sec. 1",
        ]
        for nombre in integrantes:
            self.set_x(25 + col_w + 10)
            self.cell(col_w, 6, nombre, new_x="LMARGIN", new_y="NEXT")
        y_after_int = self.get_y()
        # Mover al punto más bajo de ambas columnas
        self.set_y(max(y_after_prof, y_after_int))
        self.ln(15)
        # Ciudad y fecha centrados abajo
        self.set_font("Helvetica", "", 11)
        self.cell(0, 8, "Ciudad Guayana, Mayo 2026", align="C", new_x="LMARGIN", new_y="NEXT")

    def indice(self):
        self.add_page()
        self.start_section("Índice")
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "ÍNDICE", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_font("Helvetica", "", 11)
        items = [
            ("Introducción", 3), ("Marco Teórico: WebAssembly", 4),
            ("Mecanismos Internos de WASM", 5), ("WASM y las APIs: Mecanismos de Interacción", 8),
            ("Impacto en Tiempos de Respuesta de las API", 10),
            ("WASM en Backend: Edge Computing y Serverless", 12),
            ("Análisis Comparativo", 14), ("Casos de Uso Reales", 15),
            ("Conclusiones", 17), ("Referencias", 18),
        ]
        for titulo, pag in items:
            self.cell(0, 8, f"  {titulo} {'.' * (60 - len(titulo))} {pag}", new_x="LMARGIN", new_y="NEXT")

    def titulo_seccion(self, texto):
        self.ln(5)
        self.set_font("Helvetica", "B", 13)
        # Agregar bookmark/marcador clicable en el PDF
        self.start_section(texto)
        self.cell(0, 10, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def subtitulo(self, texto):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        # Agregar sub-bookmark
        self.start_section(texto, level=1)
        self.cell(0, 8, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def parrafo(self, texto):
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, f"        {texto}")
        self.ln(2)

    def tabla_comparativa(self):
        self.subtitulo("Tabla 1. Comparativa WASM vs JavaScript vs Contenedores")
        self.ln(3)
        self.set_font("Helvetica", "B", 9)
        cols = [("Característica", 45), ("WASM", 48), ("JavaScript", 48), ("Contenedores", 48)]
        for t, w in cols:
            self.cell(w, 8, t, border=1, align="C")
        self.ln()
        self.set_font("Helvetica", "", 8)
        filas = [
            ("Velocidad ejecución", "Cercana a nativa", "JIT, variable", "Nativa (OS)"),
            ("Cold Start", "< 50ms", "Instantáneo", "100ms - 5s"),
            ("Tamaño binario", "KB - pocos MB", "KB (texto)", "50MB - 500MB+"),
            ("Seguridad", "Sandbox estricto", "Sandbox del motor", "Aislamiento OS"),
            ("Acceso I/O", "Via WASI/host", "Nativo (Node/Browser)", "Completo"),
            ("Portabilidad", "Universal (WASM VM)", "Motor JS requerido", "Imagen por arch."),
            ("Multithreading", "SharedArrayBuffer", "Web Workers", "Nativo OS"),
            ("Mejor para APIs", "Cómputo intensivo", "I/O, CRUD, DOM", "Servicios completos"),
        ]
        for fila in filas:
            self.cell(45, 7, fila[0], border=1)
            self.cell(48, 7, fila[1], border=1, align="C")
            self.cell(48, 7, fila[2], border=1, align="C")
            self.cell(48, 7, fila[3], border=1, align="C")
            self.ln()
        self.ln(4)

    def pagina_referencias(self):
        self.add_page()
        self.titulo_seccion("Referencias")
        self.set_font("Helvetica", "", 10)
        for ref in REFERENCIAS:
            self.multi_cell(0, 5, ref)
            self.ln(2)

    def generar(self):
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=20)
        self.portada()
        self.indice()
        for seccion in SECCIONES:
            if seccion.get("nueva_pagina", False):
                self.add_page()
            self.titulo_seccion(seccion["titulo"])
            for bloque in seccion["contenido"]:
                if bloque["tipo"] == "subtitulo":
                    self.subtitulo(bloque["texto"])
                elif bloque["tipo"] == "parrafo":
                    self.parrafo(bloque["texto"])
                elif bloque["tipo"] == "tabla":
                    self.tabla_comparativa()
        self.pagina_referencias()
        self.output("Informe_WASM_API.pdf")
        print("PDF generado: Informe_WASM_API.pdf")

if __name__ == "__main__":
    pdf = InformeWASM(orientation="P", unit="mm", format="Letter")
    pdf.set_margins(25, 25, 25)
    pdf.generar()
