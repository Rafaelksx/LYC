# Asignación III: Lenguajes y Gramáticas Formales
**Materia:** Lenguaje y Compiladores (2026-I, Sección 01)  
**Universidad:** Universidad Nacional Experimental de Guayana (UNEG)  
**Profesor:** Félix Márquez  
**Autores:** Fernando Centeno (30810484), Juan Longart (31882343), Adrian Reina (31317970), Rafael Rodríguez (31882367)  
**Video de la Defensa:** [Ver Video en YouTube](https://youtu.be/PqJqbscjOgQ)  

---

Este repositorio contiene la resolución de la **Asignación III**, enfocada en el estudio práctico y formal de los lenguajes y gramáticas formales. La entrega incluye el análisis de la Jerarquía de Chomsky, el diseño y desarrollo de una gramática libre de contexto para dibujo geométrico (interpretada a SVG con motor gráfico tipo tortuga con pila), técnicas de higiene gramatical (ambigüedad, recursividad izquierda, factorización) y la implementación de un Autómata Finito Determinístico (AFD) para validar movimientos de ajedrez en notación PGN simplificada.

---

## Estructura del Proyecto en el Tema 3

```text
├── guion_exposicion.pdf    # Guión detallado para la defensa del equipo
├── informe_tema3.pdf       # Informe académico (PDF formal con el desarrollo analítico)
├── presentacion.html       # Presentación interactiva y animada en HTML
├── tema 3.pdf              # Material original de la asignatura
├── uneg-logo.png           # Logotipo institucional
├── README.md               # Este archivo instructivo
└── src/                    # Códigos fuente funcionales
    ├── dibujo_interpreter.py # Validador e intérprete gráfico de la gramática de dibujo a SVG
    └── pgn_validator.py      # Implementación del AFD para la validación de notación PGN
```

---

## Detalle de Componentes y Ejecución

### 1. Intérprete Gráfico de Gramática de Dibujo (`src/dibujo_interpreter.py`)

Este módulo implementa un motor gráfico tipo *turtle graphics* extendido con una pila para guardar y restaurar estados (posición y ángulo), lo que permite dibujar estructuras ramificadas (fractales/árboles) o figuras tridimensionales complejas.

*   **Alfabeto $\Sigma$:** `{a, c, g, t}`
*   **Mapeo de Símbolos:**
    *   `a`: Avanza dibujando una línea de longitud constante (por defecto $50$ px).
    *   `g`: Gira el cabezal $45^\circ$ en sentido horario.
    *   `c`: Guarda el estado actual en la pila (*push* de coordenadas `x`, `y` y `ángulo`).
    *   `t`: Restaura el estado desde la pila (*pop* para retornar al último punto de ramificación).
*   **Validación Sintáctica:** Verifica que la cadena contenga únicamente símbolos válidos del alfabeto y que las operaciones de pila estén balanceadas (no permitir `t` sin su correspondiente `c` previo, y asegurar que la pila quede vacía al finalizar).

#### Ejecución
Para validar las cadenas de prueba (un cuadrado, un árbol binario y un cubo en perspectiva oblicua) y exportar sus correspondientes dibujos a archivos SVG en el directorio `scratch/`, ejecuta:
```bash
python Tema3/src/dibujo_interpreter.py
```

---

### 2. Validador de Notación PGN de Ajedrez (`src/pgn_validator.py`)

Este módulo implementa un Autómata Finito Determinístico (AFD) para el reconocimiento y validación sintáctica de jugadas individuales de ajedrez bajo un subconjunto formal y simplificado del estándar PGN.

*   **Expresión Regular (Regex):**  
    $$\text{Regex} = \text{[KQRBN]}?\;\text{x}?\;\text{[a-h]}\;\text{[1-8]}\;\text{[+\#]}?$$
*   **Casos Soportados:**
    *   *Movimiento de peón:* `e4`, `d5`.
    *   *Movimiento de piezas principales:* `Nf3`, `Be7`.
    *   *Capturas:* `Bxf7`, `Nxe4` (y para peones de forma simplificada `xe4`, `xd5`).
    *   *Jaque o Jaque Mate:* `Qxe5+`, `Bxf7#`.
*   **Definición de Estados:**
    *   $q_0$: Estado inicial.
    *   $q_1$: Inicial de pieza leída (`K`, `Q`, `R`, `B`, `N`).
    *   $q_2$: Símbolo de captura leído (`x`).
    *   $q_3$: Columna de destino leída (`a-h`).
    *   $q_4$: Fila de destino leída (`1-8`) - **[Estado de Aceptación]**.
    *   $q_5$: Jaque o jaque mate leído (`+`, `#`) - **[Estado de Aceptación]**.
    *   $q_e$: Estado de error.

#### Ejecución
Para validar movimientos individuales de ajedrez y partidas completas secuenciales de prueba, ejecuta:
```bash
python Tema3/src/pgn_validator.py
```

---

## Visualización del Proyecto

*   **Presentación Interactiva:** Para ver las láminas animadas de la defensa, abre en cualquier navegador web el archivo [presentacion.html](file:///c:/Users/rafae/Desktop/LYC/Tema3/presentacion.html).
*   **Informe Técnico:** Todos los detalles teóricos, derivaciones formales paso a paso, diagramas de transición e higiene gramatical están completamente documentados en [informe_tema3.pdf](file:///c:/Users/rafae/Desktop/LYC/Tema3/informe_tema3.pdf).
