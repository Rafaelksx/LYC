# Tema 5: Análisis Sintáctico - Parsers, AST y Metacompiladores
## Universidad Nacional Experimental de Guayana
### Vicerrectorado Académico — Coordinación General de Pregrado
#### Lenguajes y Compiladores - Sección 01

* **Profesor:** Ing. Félix Márquez
* **Integrantes del Equipo:** Fernando Centeno, Juan Longart, Adrian Reina y Rafael Rodriguez
* **Ciudad Guayana, Julio de 2026** — Período Lectivo 2026-I
* **Link del video de la defensa:** https://youtu.be/kX2WFm-wvLw

---

## 📋 Descripción General del Repositorio

En este repositorio se entrega el desarrollo integral teórico-práctico del **Tema 5: Análisis Sintáctico**, fase medular del compilador donde se construye el Árbol de Sintaxis Abstracta (AST) a partir de los tokens generados por el Lexer. Exploramos a profundidad las técnicas predictivas (LL) y de desplazamiento-reducción (LR), e implementamos soluciones prácticas para lenguajes reales:
1. **Benchmark Multilingüe:** Desarrollo de parsers descendentes recursivos en Python, Node.js y Bash para analizar archivos de configuración `docker-compose.yml`, sometidos a pruebas de estrés con un generador automático.
2. **Sistema Híbrido UnegScript:** Construcción de un Lexer/Parser avanzado equipado con el algoritmo de Distancia de Levenshtein y un Mock-LLM, diseñado para actuar como un tutor sintáctico que guía en la corrección de errores tipográficos en vez de fallar de manera inmediata.

---

## 🗂️ Estructura del Repositorio (`Tema5/`)

```text
Tema5/
│
├── 📑 Análisis_Sintáctico.pdf              # Informe final académico y detallado con todas las actividades
├── 📖 README.md                            # Guía principal del repositorio (este archivo)
├── 📄 tema 5.pdf                           # Documento oficial con la asignación del tema
├── 🖥️ presentacion_tema5.html              # Presentación interactiva en HTML (Diseño Dark Cyberpunk)
│
├── 📂 actividad_teorica/                   # Investigación Teórica
│   └── conceptos_parser.md                 # AST, Parsers LL vs LR, Metacompiladores, Manejo de Errores
│
├── 📂 actividad4_benchmark/                # Actividad 4: Benchmark Docker Compose
│   ├── compose_parser_python.py            # Parser en Python
│   ├── compose_parser_node.js              # Parser en Node.js
│   ├── compose_parser_bash.sh              # Parser en Bash
│   ├── run_benchmark.py                    # Script automatizado generador de archivos y medidor de tiempos
│   └── benchmark_resultado.png             # Gráfica de resultados experimentales
│
└── 📂 actividad5_hibrido/                  # Actividad 5: UnegScript con Levenshtein y Fallback IA
    └── unegscript_parser.py                # Lexer y Parser interactivo con análisis semántico preventivo
```

---

## 🚀 Guía Rápida de Ejecución de las Actividades

### 1️⃣ Ejecutar el Benchmark de Parsers (`Actividad 4`)
Ingresa a la carpeta `actividad4_benchmark` y ejecuta el script orquestador en Python. Este creará 16 archivos sintéticos de Docker Compose y los parseará usando los 3 lenguajes para medir su eficiencia real en tiempo O(n):
```bash
cd actividad4_benchmark
python run_benchmark.py
```

### 2️⃣ Demostración del Parser Híbrido UnegScript (`Actividad 5`)
Para observar cómo nuestro compilador interactúa como tutor al detectar errores de sintaxis (`whlie`, `pront`, `retrun`), asegúrate de tener Python instalado y ejecuta:
```bash
cd actividad5_hibrido
python unegscript_parser.py
```
*Se mostrará en consola el análisis token por token, el cálculo de distancia de Levenshtein, las recomendaciones de la IA simulada y el estado final de construcción del AST.*
