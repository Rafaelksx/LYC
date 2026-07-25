#!/usr/bin/env bash
# =====================================================================
# Actividad 4 – Tema 5: Análisis Sintáctico
# Parser de docker-compose.yml en Bash (lenguaje 3)
# Universidad Nacional Experimental de Guayana (UNEG)
# Lenguajes y Compiladores
# =====================================================================
# Este parser analiza sintácticamente un archivo docker-compose.yml
# usando herramientas nativas de Bash (grep, sed, awk) y construye
# una representación textual del AST como árbol indentado.
# =====================================================================

set -euo pipefail

# ─────────────────────────────────────────────────────────────
# Colores ANSI
# ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────
# Variables globales
# ─────────────────────────────────────────────────────────────
ARCHIVO="${1:-docker-compose.yml}"
ERRORES=0
WARNINGS=0
TOKENS=0
declare -a LISTA_ERRORES=()

# ─────────────────────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────────────────────
registrar_error() {
  ERRORES=$((ERRORES + 1))
  LISTA_ERRORES+=("$1")
}

registrar_warning() {
  WARNINGS=$((WARNINGS + 1))
  echo -e "  ${YELLOW}⚠ WARN: $1${NC}"
}

imprimir_nodo() {
  local nivel="$1"
  local tipo="$2"
  local valor="$3"
  local indent
  indent=$(printf '%0.s  ' $(seq 1 "$nivel"))
  echo "${indent}[${tipo}] ${valor}"
}

# ─────────────────────────────────────────────────────────────
# Verificar que el archivo existe
# ─────────────────────────────────────────────────────────────
if [[ ! -f "$ARCHIVO" ]]; then
  echo -e "${RED}❌ Archivo no encontrado: $ARCHIVO${NC}"
  exit 1
fi

LINEAS=$(wc -l < "$ARCHIVO")
T_INICIO=$(date +%s%3N)

echo ""
echo "============================================================"
echo " Parser Bash → $ARCHIVO"
echo "============================================================"
echo ""
echo "[DockerCompose] \"root\""

# ─────────────────────────────────────────────────────────────
# ANÁLISIS LEXICOGRÁFICO + SINTÁCTICO
# ─────────────────────────────────────────────────────────────
num_linea=0
contexto=""          # Qué sección estamos parseando
servicio_actual=""   # Nombre del servicio en curso

while IFS= read -r linea || [[ -n "$linea" ]]; do
  num_linea=$((num_linea + 1))

  # Ignorar comentarios y líneas vacías
  if [[ "$linea" =~ ^[[:space:]]*# ]] || [[ -z "${linea// }" ]]; then
    continue
  fi

  TOKENS=$((TOKENS + 1))

  # ── Nivel 0: Directivas raíz ──────────────────────────────
  if [[ "$linea" =~ ^version[[:space:]]*: ]]; then
    version=$(echo "$linea" | sed "s/version[[:space:]]*:[[:space:]]*//" | tr -d "'\"")
    imprimir_nodo 1 "Version" "$version"
    contexto="root"

  elif [[ "$linea" =~ ^services[[:space:]]*: ]]; then
    imprimir_nodo 1 "Servicios" ""
    contexto="services"

  elif [[ "$linea" =~ ^networks[[:space:]]*: ]]; then
    imprimir_nodo 1 "Redes" ""
    contexto="networks"

  elif [[ "$linea" =~ ^volumes[[:space:]]*: ]]; then
    imprimir_nodo 1 "Volúmenes" ""
    contexto="volumes"

  # ── Nivel 1: Nombre de servicio (2 espacios de indentación) ─
  elif [[ "$contexto" == "services" ]] && [[ "$linea" =~ ^[[:space:]]{2}[a-zA-Z0-9_-]+[[:space:]]*: ]]; then
    servicio_actual=$(echo "$linea" | sed 's/[[:space:]]//g; s/://')
    imprimir_nodo 2 "Servicio" "$servicio_actual"

  # ── Nivel 2: Directivas de servicio (4+ espacios) ───────────
  elif [[ "$contexto" == "services" ]] && [[ "$linea" =~ ^[[:space:]]{4,}image[[:space:]]*: ]]; then
    img=$(echo "$linea" | sed 's/.*image[[:space:]]*:[[:space:]]*//')
    imprimir_nodo 3 "Image" "$img"

  elif [[ "$contexto" == "services" ]] && [[ "$linea" =~ ^[[:space:]]{4,}build[[:space:]]*: ]]; then
    build_val=$(echo "$linea" | sed 's/.*build[[:space:]]*:[[:space:]]*//')
    imprimir_nodo 3 "Build" "$build_val"

  elif [[ "$contexto" == "services" ]] && [[ "$linea" =~ ^[[:space:]]{4,}restart[[:space:]]*: ]]; then
    rst=$(echo "$linea" | sed 's/.*restart[[:space:]]*:[[:space:]]*//')
    imprimir_nodo 3 "Restart" "$rst"

  elif [[ "$contexto" == "services" ]] && [[ "$linea" =~ ^[[:space:]]{4,}command[[:space:]]*: ]]; then
    cmd=$(echo "$linea" | sed 's/.*command[[:space:]]*:[[:space:]]*//')
    imprimir_nodo 3 "Command" "$cmd"

  elif [[ "$contexto" == "services" ]] && \
       [[ "$linea" =~ ^[[:space:]]{4,}(ports|environment|depends_on)[[:space:]]*: ]]; then
    directiva=$(echo "$linea" | grep -oE '(ports|environment|depends_on)' | head -1)
    imprimir_nodo 3 "${directiva^}" ""

  # ── Ítems de lista ───────────────────────────────────────────
  elif [[ "$linea" =~ ^[[:space:]]+-[[:space:]]+ ]]; then
    item=$(echo "$linea" | sed 's/^[[:space:]]*-[[:space:]]*//')
    imprimir_nodo 4 "Item" "$item"

  # ── Propiedad genérica ────────────────────────────────────────
  elif [[ "$linea" =~ ^[[:space:]]+[a-zA-Z0-9_-]+[[:space:]]*:.*$ ]]; then
    imprimir_nodo 3 "Propiedad" "${linea// /}"

  # ── Token inesperado ──────────────────────────────────────────
  else
    registrar_error "Línea ${num_linea}: Estructura inesperada → '${linea}'"
  fi

done < "$ARCHIVO"

T_FIN=$(date +%s%3N)
TIEMPO_MS=$((T_FIN - T_INICIO))

# ─────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────
echo ""
echo "------------------------------------------------------------"
echo " RESUMEN DEL ANÁLISIS"
echo "------------------------------------------------------------"
printf "  Archivo     : %s\n" "$ARCHIVO"
printf "  Líneas      : %s\n" "$LINEAS"
printf "  Tokens      : %s\n" "$TOKENS"
printf "  Errores     : %s\n" "$ERRORES"
printf "  Warnings    : %s\n" "$WARNINGS"
printf "  Tiempo      : %s ms\n" "$TIEMPO_MS"

if [[ $ERRORES -eq 0 ]]; then
  echo -e "  Estado      : ${GREEN}ACEPTADO ✅${NC}"
else
  echo -e "  Estado      : ${RED}RECHAZADO ❌${NC}"
  echo ""
  echo "  Errores encontrados:"
  for err in "${LISTA_ERRORES[@]}"; do
    echo -e "    ${RED}⚠ $err${NC}"
  done
fi

echo "============================================================"
echo ""
