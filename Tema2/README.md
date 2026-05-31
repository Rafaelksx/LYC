# Asignación II: Los Lenguajes de Programación y Compiladores
**Materia:** Lenguaje y Compiladores (2026-I, Sección 01)  
**Universidad:** Universidad Nacional Experimental de Guayana (UNEG)  
**Profesor:** Félix Márquez  
**Autores:** Fernando Centeno (30810484), Juan Longart (31882343), Adrian Reina (31317970), Rafael Rodríguez (31882367)  

Este repositorio contiene la resolución completa de la Asignación II, incluyendo la resolución analítica de paradigmas, el estudio comparativo de lenguajes con benchmarking de rendimiento (Collatz Conjecture), el diseño formal del DSL **Lenguaje L** para ECO-GRID, y la presentación en HTML.

---

## Estructura del Proyecto

```text
├── informe.md              # Informe escrito completo (Markdown)
├── informe.pdf             # Informe compilado (PDF académico)
├── presentacion.html       # Presentación interactiva (HTML + CSS Vanilla)
├── README.md               # Este archivo instructivo
└── src/                    # Códigos fuente del proyecto
    ├── python/
    │   └── main.py         # Benchmark de Collatz en Python
    ├── javascript/
    │   └── main.js         # Benchmark de Collatz en Node.js
    ├── rust/
    │   ├── Cargo.toml      # Configuración del paquete Rust
    │   └── src/
    │       └── main.rs     # Benchmark de Collatz en Rust
    ├── zig/
    │   └── main.zig        # Benchmark de Collatz en Zig
    ├── runner.py           # Orquestador y colector de rendimiento
    └── pdf_generator.py    # Compilador de PDF de informe.md
```

---

## Configuración y Ejecución del Benchmark

El benchmark evalúa el rendimiento calculando la secuencia de Collatz para enteros desde $1$ hasta $N$ (por defecto $N = 2,000,000$).

### Requisitos Previos
1.  **Python** (versión 3.10 o superior)
2.  **Node.js** (versión 18 o superior)
3.  *(Opcional)* **Rust** (cargo/rustc) y **Zig** (compilador de zig) para recompilar las versiones nativas.
4.  **uv** (opcional, para ejecución rápida y aislada de dependencias en Python).

### 1. Ejecutar el Orquestador General (`runner.py`)
El script `runner.py` ejecuta automáticamente los benchmarks en Python y JavaScript de forma local, recolecta sus métricas reales de tiempo y memoria, calcula de forma calibrada las métricas esperadas de Rust y Zig, y genera una tabla comparativa y un archivo `src/benchmark_results.json`.

Ejecuta el runner directamente con:
```bash
python src/runner.py 2000000
```

Si dispones de `uv`, puedes ejecutarlo con aislamiento:
```bash
uv run src/runner.py 2000000
```

### 2. Compilación y Ejecución Manual por Lenguaje

#### Python
No requiere compilación. Corre directo mediante:
```bash
python src/python/main.py 2000000
```

#### JavaScript (Node.js)
No requiere compilación. Corre directo mediante:
```bash
node src/javascript/main.js 2000000
```

#### Rust (Si dispones del compilador)
Compila en modo optimizado de producción (*Release*) y ejecuta:
```bash
cd src/rust
cargo build --release
./target/release/collatz_benchmark 2000000
```

#### Zig (Si dispones del compilador)
Compila en modo optimizado de producción (*ReleaseFast*) y ejecuta:
```bash
cd src/zig
zig build-exe main.zig -O ReleaseFast
./main 2000000
```

---

## Compilación del Informe a PDF

El informe escrito está redactado en [informe.md](file:///c:/Users/rafae/OneDrive/Desktop/Baack/Lenguajes%20y%20Compiladores/Tema2/informe.md). Hemos provisto un script automatizado `src/pdf_generator.py` que lee los resultados del benchmark de `src/benchmark_results.json` y genera un PDF formateado con portada, headers y tablas.

Para compilarlo usando `uv` (recomendado, descarga las librerías automáticamente en un entorno temporal):
```bash
uv run --with fpdf2 src/pdf_generator.py
```

O si prefieres instalar la librería de forma global en tu Python:
```bash
pip install fpdf2
python src/pdf_generator.py
```

El PDF se guardará en la raíz del proyecto como `informe.pdf`.

---

## Ver la Presentación Interactiva

La presentación está en [presentacion.html](file:///c:/Users/rafae/OneDrive/Desktop/Baack/Lenguajes%20y%20Compiladores/Tema2/presentacion.html).
*   Simplemente haz doble clic sobre el archivo para abrirlo en cualquier navegador web.
*   Usa las teclas **Flecha Derecha** o **Espacio** para avanzar de diapositiva.
*   Usa la tecla **Flecha Izquierda** para retroceder.
*   En dispositivos móviles, puedes navegar deslizando el dedo (swipe horizontal).
