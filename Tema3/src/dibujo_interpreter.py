import math
import os
import sys

class DibujoInterpreter:
    def __init__(self, step_size=50):
        self.step_size = step_size

    def validate(self, string):
        """
        Valida que la cadena contenga únicamente símbolos del alfabeto {a, c, g, t}
        y que las operaciones de pila (c = push, t = pop) estén balanceadas.
        """
        stack_depth = 0
        for i, char in enumerate(string):
            if char not in {'a', 'c', 'g', 't'}:
                return False, f"Carácter inválido '{char}' en la posición {i}."
            if char == 'c':
                stack_depth += 1
            elif char == 't':
                stack_depth -= 1
                if stack_depth < 0:
                    return False, f"Error de pila: 't' (pop) sin un 'c' (push) previo en la posición {i}."
        
        if stack_depth != 0:
            return False, f"Error de pila: Quedaron {stack_depth} estados sin restaurar al final de la cadena."
        
        return True, "Cadena válida."

    def interpret(self, string, output_svg_path):
        """
        Interpreta la cadena y genera un archivo SVG con el dibujo.
        Mapeo:
          a: Avanzar dibujando step_size unidades.
          g: Girar a la derecha 45 grados.
          c: Guardar estado actual (x, y, ángulo) en la pila.
          t: Restaurar estado actual (x, y, ángulo) desde la pila.
        """
        is_valid, msg = self.validate(string)
        if not is_valid:
            raise ValueError(f"Cadena inválida: {msg}")

        # Estado inicial
        x, y = 0.0, 0.0
        angle = 90.0  # Iniciamos mirando hacia arriba (90 grados)
        stack = []
        lines = []

        # Registrar los puntos para calcular la caja de delimitación (bounding box)
        points = [(x, y)]

        for char in string:
            if char == 'a':
                rad = math.radians(angle)
                nx = x + self.step_size * math.cos(rad)
                ny = y + self.step_size * math.sin(rad)
                # Guardamos la línea (invertimos y para que SVG dibuje hacia arriba)
                lines.append((x, y, nx, ny))
                x, y = nx, ny
                points.append((x, y))
            elif char == 'g':
                angle = (angle - 45.0) % 360.0
            elif char == 'c':
                stack.append((x, y, angle))
            elif char == 't':
                if stack:
                    x, y, angle = stack.pop()
                    points.append((x, y))

        if not lines:
            # Si no hay líneas, dibujamos un punto por defecto
            lines.append((0, 0, 0, 0))

        # Calcular bounding box para definir el viewBox de SVG
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y

        # Añadir un margen alrededor del dibujo
        margin = 20
        view_x = min_x - margin
        # Invertimos el eje y en SVG para que las coordenadas cartesianas estándar
        # (donde y sube) se muestren correctamente (en SVG, y baja).
        # Para ello, mapeamos y_svg = max_y - y + min_y
        view_y = -(max_y + margin)
        view_w = width + 2 * margin
        view_h = height + 2 * margin

        # Si el dibujo es un solo punto, forzamos un tamaño mínimo
        if view_w <= 2 * margin: view_w = 100
        if view_h <= 2 * margin: view_h = 100

        # Crear SVG content
        svg_content = []
        svg_content.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_x} {view_y} {view_w} {view_h}" width="100%" height="100%">')
        svg_content.append('  <!-- Fondo blanco para el dibujo -->')
        svg_content.append(f'  <rect x="{view_x}" y="{view_y}" width="{view_w}" height="{view_h}" fill="#fcfcfc" rx="5"/>')
        svg_content.append('  <g stroke="#2c3e50" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none">')

        for l in lines:
            x1, y1, x2, y2 = l
            # Invertimos el eje Y para que suba
            svg_content.append(f'    <line x1="{x1:.2f}" y1="{-y1:.2f}" x2="{x2:.2f}" y2="{-y2:.2f}" />')

        # Si es un árbol, podemos añadir círculos verdes en los extremos (hojas) para darle estética premium
        # Pero nos apegamos al trazo puro para mostrar la exactitud del modelado.
        
        svg_content.append('  </g>')
        svg_content.append('</svg>')

        # Crear directorio padre si no existe
        os.makedirs(os.path.dirname(os.path.abspath(output_svg_path)), exist_ok=True)
        with open(output_svg_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))
        
        print(f"Dibujo exportado a SVG exitosamente en: {output_svg_path}")

if __name__ == "__main__":
    interpreter = DibujoInterpreter()
    
    # Definición de las cadenas de los casos prácticos
    # 1. Cuadrado: avanza, gira 90 (g g) y repite (aggaggaggagga)
    cuadrado_str = "aggaggaggagga"
    
    # 2. Árbol binario: tronco (a), rama izquierda, rama derecha
    arbol_str = "acgggggggacgggggggatcgattcgacgggggggatcgatt"
    
    # 3. Cubo en proyección oblicua: frente, 4 diagonales en esquinas, y fondo
    cubo_str = "cgatacgatggaggggggcgatggggaggggcgatggggggagggagggggggagggaggagga"

    print("Validando cadenas de prueba:")
    for name, s in [("Cuadrado", cuadrado_str), ("Arbol", arbol_str), ("Cubo", cubo_str)]:
        val, msg = interpreter.validate(s)
        print(f"- {name}: {msg} ({s})")
        if val:
            interpreter.interpret(s, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scratch", f"{name.lower()}.svg"))
