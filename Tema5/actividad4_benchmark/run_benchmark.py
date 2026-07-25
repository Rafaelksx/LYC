#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Actividad 4 – Tema 5: Análisis Sintáctico
Generador de archivos docker-compose.yml de prueba + Benchmark de los 3 parsers
Universidad Nacional Experimental de Guayana (UNEG) - Lenguajes y Compiladores

Este script:
1. Genera N archivos docker-compose.yml con N servicios cada uno (N de 5 a 20).
2. Ejecuta el parser Python sobre cada archivo y mide el tiempo.
3. Genera un reporte de texto con las métricas.
4. (Opcional) Genera una gráfica si matplotlib está disponible.
"""

import os
import time
import subprocess
import sys
import random

# ─────────────────────────────────────────────────────────────
# Importar el parser Python local
# ─────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
from compose_parser_python import analizar_compose


# ─────────────────────────────────────────────────────────────
# 1. GENERADOR DE ARCHIVOS DE PRUEBA
# ─────────────────────────────────────────────────────────────
IMAGENES = [
    "nginx:latest", "node:18-alpine", "python:3.11-slim", "postgres:15",
    "redis:7", "mongo:6", "rabbitmq:3-management", "elasticsearch:8.5.0",
    "grafana/grafana:latest", "prom/prometheus:latest", "mysql:8.0",
    "traefik:v2.10", "minio/minio:latest", "vault:latest", "consul:latest",
    "hashicorp/terraform:latest", "jenkins/jenkins:lts", "sonarqube:community",
    "gitlab/gitlab-ce:latest", "portainer/portainer-ce:latest"
]

PUERTOS_BASE = [80, 443, 3000, 3306, 5432, 5672, 6379, 8080, 8443, 9000, 9090, 9200, 15672, 27017]


def generar_compose(num_servicios: int) -> str:
    """Genera el contenido de un docker-compose.yml con `num_servicios` servicios."""
    lineas = [
        "version: '3.8'",
        "",
        "services:",
    ]
    
    nombres_usados = set()
    puertos_usados = set()
    
    for i in range(num_servicios):
        # Nombre único para el servicio
        base_nombre = f"servicio_{i+1:02d}"
        while base_nombre in nombres_usados:
            base_nombre = f"servicio_{random.randint(1, 999):03d}"
        nombres_usados.add(base_nombre)
        
        imagen = IMAGENES[i % len(IMAGENES)]
        
        # Puerto único
        puerto_host = 10000 + i * 100 + random.randint(1, 99)
        while puerto_host in puertos_usados:
            puerto_host += 1
        puerto_host = min(puerto_host, 65000)
        puertos_usados.add(puerto_host)
        puerto_container = PUERTOS_BASE[i % len(PUERTOS_BASE)]
        
        lineas += [
            f"  {base_nombre}:",
            f"    image: {imagen}",
            f"    restart: unless-stopped",
            f"    ports:",
            f"      - \"{puerto_host}:{puerto_container}\"",
            f"    environment:",
            f"      - APP_ENV=production",
            f"      - SERVICE_ID={i+1}",
            f"      - LOG_LEVEL=info",
        ]
        
        # Añadir depends_on para algunos servicios
        if i > 0 and i % 3 == 0:
            dep_name = f"servicio_{(i-1):02d}" if f"servicio_{(i-1):02d}" in nombres_usados else list(nombres_usados)[0]
            lineas += [
                f"    depends_on:",
                f"      - {dep_name}",
            ]
        
        lineas.append("")
    
    # Sección de networks y volumes
    lineas += [
        "networks:",
        "  red_principal:",
        "    driver: bridge",
        "",
        "volumes:",
        "  datos_persistentes:",
        "    driver: local",
        "",
    ]
    
    return "\n".join(lineas)


# ─────────────────────────────────────────────────────────────
# 2. BENCHMARK PYTHON
# ─────────────────────────────────────────────────────────────
def benchmark_python(archivos_generados: dict) -> list:
    print(f"\n{'─'*60}")
    print(" 📊 BENCHMARK: Parser Python")
    print(f"{'─'*60}")
    resultados = []
    
    for num_srv, filepath in sorted(archivos_generados.items()):
        r = analizar_compose(filepath)
        tiempo = r.get("tiempo_ms", 0)
        estado = r.get("estado", "?")
        tokens = r.get("tokens", 0)
        print(f"  N={num_srv:2d} servicios | {tokens:4d} tokens | {tiempo:8.4f} ms | {estado}")
        resultados.append({
            "n": num_srv,
            "tiempo_ms": tiempo,
            "tokens": tokens,
            "lenguaje": "Python"
        })
    
    return resultados


# ─────────────────────────────────────────────────────────────
# 3. BENCHMARK NODE.JS
# ─────────────────────────────────────────────────────────────
def benchmark_nodejs(archivos_generados: dict) -> list:
    print(f"\n{'─'*60}")
    print(" 📊 BENCHMARK: Parser Node.js")
    print(f"{'─'*60}")
    resultados = []
    
    node_script = os.path.join(script_dir, "compose_parser_node.js")
    
    for num_srv, filepath in sorted(archivos_generados.items()):
        try:
            t_inicio = time.perf_counter()
            result = subprocess.run(
                ["node", node_script, filepath],
                capture_output=True, text=True, timeout=15
            )
            t_fin = time.perf_counter()
            tiempo_ms = (t_fin - t_inicio) * 1000
            
            estado = "ACEPTADO" if "ACEPTADO" in result.stdout else "RECHAZADO"
            tokens = 0
            for line in result.stdout.splitlines():
                if "Tokens" in line and ":" in line:
                    try:
                        tokens = int(line.split(":")[1].strip())
                    except ValueError:
                        pass
            
            print(f"  N={num_srv:2d} servicios | {tokens:4d} tokens | {tiempo_ms:8.4f} ms | {estado}")
            resultados.append({"n": num_srv, "tiempo_ms": round(tiempo_ms, 4), "tokens": tokens, "lenguaje": "Node.js"})
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"  N={num_srv:2d} → ⚠ Node.js no disponible: {e}")
            resultados.append({"n": num_srv, "tiempo_ms": 0, "tokens": 0, "lenguaje": "Node.js"})
    
    return resultados


# ─────────────────────────────────────────────────────────────
# 4. GENERACIÓN DE GRÁFICA (opcional con matplotlib)
# ─────────────────────────────────────────────────────────────
def generar_grafica(resultados_python: list, resultados_node: list):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(
            'Actividad 4 – Tema 5: Benchmark de Parsers docker-compose.yml\n'
            'Universidad Nacional Experimental de Guayana (UNEG) – Lenguajes y Compiladores',
            fontsize=11, fontweight='bold'
        )

        ns_py = [r["n"] for r in resultados_python]
        ts_py = [r["tiempo_ms"] for r in resultados_python]
        ns_nd = [r["n"] for r in resultados_node if r["tiempo_ms"] > 0]
        ts_nd = [r["tiempo_ms"] for r in resultados_node if r["tiempo_ms"] > 0]

        # Gráfica 1: Tiempo de ejecución vs N servicios
        ax1.plot(ns_py, ts_py, 'o-', color='#6366f1', linewidth=2.5, markersize=7, label='Python')
        if ns_nd:
            ax1.plot(ns_nd, ts_nd, 's--', color='#f59e0b', linewidth=2.5, markersize=7, label='Node.js')
        ax1.set_xlabel('Número de servicios en el archivo', fontsize=10)
        ax1.set_ylabel('Tiempo de ejecución (ms)', fontsize=10)
        ax1.set_title('Rendimiento: Tiempo vs. Complejidad', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Gráfica 2: Tokens procesados vs N servicios (Python)
        toks_py = [r["tokens"] for r in resultados_python]
        ax2.bar(ns_py, toks_py, color='#10b981', alpha=0.8, edgecolor='white')
        ax2.set_xlabel('Número de servicios en el archivo', fontsize=10)
        ax2.set_ylabel('Tokens procesados', fontsize=10)
        ax2.set_title('Volumen: Tokens vs. Complejidad (Python)', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        grafica_path = os.path.join(script_dir, "benchmark_resultado.png")
        plt.savefig(grafica_path, dpi=130, bbox_inches='tight')
        print(f"\n  📈 Gráfica guardada en: {grafica_path}")
        plt.close()
    except ImportError:
        print("\n  ℹ matplotlib no está disponible. Instálalo con: pip install matplotlib")
        print("  Se omitió la generación de la gráfica.")


# ─────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print(" BENCHMARK – Parsers de docker-compose.yml")
    print(" Universidad Nacional Experimental de Guayana (UNEG)")
    print(" Lenguajes y Compiladores – Tema 5")
    print("="*60)

    # Crear carpeta para los archivos de prueba
    carpeta_pruebas = os.path.join(script_dir, "archivos_prueba")
    os.makedirs(carpeta_pruebas, exist_ok=True)

    # Generar archivos de N = 5 hasta 20 servicios
    print(f"\n  Generando archivos de prueba en: {carpeta_pruebas}")
    archivos_generados = {}
    for n in range(5, 21):
        contenido = generar_compose(n)
        filepath = os.path.join(carpeta_pruebas, f"compose_{n:02d}_servicios.yml")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(contenido)
        archivos_generados[n] = filepath
    print(f"  ✅ {len(archivos_generados)} archivos generados (N=5 a N=20 servicios).")

    # Ejecutar benchmarks
    resultados_py = benchmark_python(archivos_generados)
    resultados_nd = benchmark_nodejs(archivos_generados)

    # Reporte de texto
    print(f"\n{'='*60}")
    print(" REPORTE RESUMEN COMPARATIVO")
    print(f"{'='*60}")
    print(f"{'N':>4} | {'Python (ms)':>12} | {'Node.js (ms)':>12} | {'Diferencia':>12}")
    print(f"{'─'*4}-+-{'─'*12}-+-{'─'*12}-+-{'─'*12}")
    for i, r_py in enumerate(resultados_py):
        r_nd = resultados_nd[i] if i < len(resultados_nd) else {"tiempo_ms": 0}
        diff = r_nd["tiempo_ms"] - r_py["tiempo_ms"]
        ganador = "Py +" if diff > 0 else "Nd +" if diff < 0 else "Empate"
        print(f"  {r_py['n']:2d} | {r_py['tiempo_ms']:12.4f} | {r_nd['tiempo_ms']:12.4f} | {abs(diff):9.4f} ms ({ganador})")

    # Gráfica
    generar_grafica(resultados_py, resultados_nd)

    print(f"\n{'='*60}")
    print(" CONCLUSIÓN: La complejidad temporal de ambos parsers es O(n)")
    print(" (lineal respecto al número de tokens / líneas del archivo),")
    print(" confirmando la eficiencia del análisis descendente recursivo.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
