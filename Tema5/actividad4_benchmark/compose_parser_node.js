#!/usr/bin/env node
// =====================================================================
// Actividad 4 – Tema 5: Análisis Sintáctico
// Parser de docker-compose.yml en Node.js (JavaScript)
// Universidad Nacional Experimental de Guayana (UNEG)
// Lenguajes y Compiladores
// =====================================================================

'use strict';

const fs = require('fs');

// ─────────────────────────────────────────────────────────────
// 1. DEFINICIÓN DE TOKENS
// ─────────────────────────────────────────────────────────────
const TOKEN_RULES = [
  { tipo: 'VERSION',     patron: /^version\s*:/ },
  { tipo: 'SERVICES',    patron: /^services\s*:/ },
  { tipo: 'NETWORKS',    patron: /^networks\s*:/ },
  { tipo: 'VOLUMES',     patron: /^volumes\s*:/ },
  { tipo: 'IMAGE',       patron: /^\s{2,}image\s*:/ },
  { tipo: 'BUILD',       patron: /^\s{2,}build\s*:/ },
  { tipo: 'PORTS',       patron: /^\s{2,}ports\s*:/ },
  { tipo: 'ENVIRONMENT', patron: /^\s{2,}environment\s*:/ },
  { tipo: 'DEPENDS_ON',  patron: /^\s{2,}depends_on\s*:/ },
  { tipo: 'COMMAND',     patron: /^\s{2,}command\s*:/ },
  { tipo: 'RESTART',     patron: /^\s{2,}restart\s*:/ },
  { tipo: 'SERVICE_NAME',patron: /^\s{2}[a-zA-Z0-9_\-]+\s*:/ },
  { tipo: 'LIST_ITEM',   patron: /^\s+-\s+.+/ },
  { tipo: 'KEY_VALUE',   patron: /^\s+[a-zA-Z0-9_\-]+\s*:.*/ },
  { tipo: 'COMMENT',     patron: /^\s*#.*/ },
  { tipo: 'BLANK',       patron: /^\s*$/ },
  { tipo: 'UNKNOWN',     patron: /.+/ },
];

// ─────────────────────────────────────────────────────────────
// 2. LEXER
// ─────────────────────────────────────────────────────────────
function tokenizar(contenido) {
  const tokens = [];
  const lineas = contenido.split('\n');
  lineas.forEach((linea, idx) => {
    const numLinea = idx + 1;
    for (const regla of TOKEN_RULES) {
      if (regla.patron.test(linea)) {
        if (regla.tipo !== 'COMMENT' && regla.tipo !== 'BLANK') {
          tokens.push({ tipo: regla.tipo, valor: linea.trim(), linea: numLinea });
        }
        break;
      }
    }
  });
  return tokens;
}

// ─────────────────────────────────────────────────────────────
// 3. NODO AST
// ─────────────────────────────────────────────────────────────
function crearNodo(tipo, valor = '', hijos = []) {
  return { tipo, valor, hijos };
}

function imprimirAST(nodo, nivel = 0) {
  const indent = '  '.repeat(nivel);
  let resultado = `${indent}[${nodo.tipo}] ${JSON.stringify(nodo.valor)}\n`;
  for (const hijo of nodo.hijos) {
    resultado += imprimirAST(hijo, nivel + 1);
  }
  return resultado;
}

// ─────────────────────────────────────────────────────────────
// 4. PARSER DESCENDENTE RECURSIVO
// ─────────────────────────────────────────────────────────────
class ParserDockerCompose {
  constructor(tokens) {
    this.tokens = tokens;
    this.pos = 0;
    this.errores = [];
    this.warnings = [];
  }

  actual() {
    return this.pos < this.tokens.length ? this.tokens[this.pos] : null;
  }

  consumir(tipoEsperado = null) {
    const tok = this.actual();
    if (!tok) return null;
    if (tipoEsperado && tok.tipo !== tipoEsperado) {
      this.errores.push(
        `Línea ${tok.linea}: Se esperaba '${tipoEsperado}' pero se encontró '${tok.tipo}' → '${tok.valor}'`
      );
    }
    this.pos++;
    return tok;
  }

  parsear() {
    const raiz = crearNodo('DockerCompose');

    if (this.actual() && this.actual().tipo === 'VERSION') {
      const tok = this.consumir('VERSION');
      const partes = tok.valor.split(':');
      const version = partes.length > 1 ? partes[1].trim().replace(/['"]/g, '') : '?';
      raiz.hijos.push(crearNodo('Version', version));
    } else {
      this.warnings.push("Advertencia: No se encontró directiva 'version'.");
    }

    while (this.actual()) {
      const tok = this.actual();
      if (tok.tipo === 'SERVICES') {
        raiz.hijos.push(this.parsearServicios());
      } else if (tok.tipo === 'NETWORKS') {
        raiz.hijos.push(this.parsearSeccionSimple('Redes'));
      } else if (tok.tipo === 'VOLUMES') {
        raiz.hijos.push(this.parsearSeccionSimple('Volúmenes'));
      } else {
        this.errores.push(`Línea ${tok.linea}: Token inesperado '${tok.tipo}' a nivel raíz.`);
        this.pos++;
      }
    }

    return raiz;
  }

  parsearServicios() {
    this.consumir('SERVICES');
    const nodo = crearNodo('Servicios');
    while (this.actual() && this.actual().tipo === 'SERVICE_NAME') {
      nodo.hijos.push(this.parsearUnServicio());
    }
    return nodo;
  }

  parsearUnServicio() {
    const tok = this.consumir('SERVICE_NAME');
    const nombre = tok.valor.replace(/:$/, '').trim();
    const nodo = crearNodo('Servicio', nombre);

    const directivasServicio = new Set([
      'IMAGE', 'BUILD', 'PORTS', 'ENVIRONMENT',
      'DEPENDS_ON', 'COMMAND', 'RESTART', 'KEY_VALUE', 'LIST_ITEM'
    ]);

    while (this.actual() && directivasServicio.has(this.actual().tipo)) {
      const t = this.actual();
      if (['PORTS', 'ENVIRONMENT', 'DEPENDS_ON'].includes(t.tipo)) {
        nodo.hijos.push(this.parsearLista(t.tipo));
      } else if (t.tipo === 'IMAGE') {
        const ti = this.consumir('IMAGE');
        const val = ti.valor.includes(':') ? ti.valor.split(':').slice(1).join(':').trim() : '?';
        nodo.hijos.push(crearNodo('Image', val));
      } else if (t.tipo === 'RESTART') {
        const tr = this.consumir('RESTART');
        const val = tr.valor.includes(':') ? tr.valor.split(':')[1].trim() : '?';
        nodo.hijos.push(crearNodo('Restart', val));
      } else if (t.tipo === 'COMMAND') {
        const tc = this.consumir('COMMAND');
        const val = tc.valor.includes(':') ? tc.valor.split(':').slice(1).join(':').trim() : '?';
        nodo.hijos.push(crearNodo('Command', val));
      } else {
        const tg = this.consumir();
        nodo.hijos.push(crearNodo('Propiedad', tg.valor));
      }
    }

    return nodo;
  }

  parsearLista(tipo) {
    const tokHeader = this.consumir(tipo);
    const nodo = crearNodo(tipo.charAt(0) + tipo.slice(1).toLowerCase(), tokHeader.valor.replace(/:$/, '').trim());
    while (this.actual() && this.actual().tipo === 'LIST_ITEM') {
      const tokItem = this.consumir('LIST_ITEM');
      nodo.hijos.push(crearNodo('Item', tokItem.valor.replace(/^\s*-\s*/, '').trim()));
    }
    return nodo;
  }

  parsearSeccionSimple(nombre) {
    this.consumir();
    const nodo = crearNodo(nombre);
    const tiposValidos = new Set(['KEY_VALUE', 'LIST_ITEM', 'SERVICE_NAME']);
    while (this.actual() && tiposValidos.has(this.actual().tipo)) {
      const tok = this.consumir();
      nodo.hijos.push(crearNodo('Entrada', tok.valor));
    }
    return nodo;
  }
}

// ─────────────────────────────────────────────────────────────
// 5. FUNCIÓN PRINCIPAL
// ─────────────────────────────────────────────────────────────
function analizarCompose(filepath) {
  const tInicio = performance.now ? performance.now() : Date.now();

  let contenido;
  try {
    contenido = fs.readFileSync(filepath, 'utf-8');
  } catch (e) {
    return { error: `Archivo no encontrado: ${filepath}`, tiempo_ms: 0 };
  }

  const tokens = tokenizar(contenido);
  const parser = new ParserDockerCompose(tokens);
  const ast = parser.parsear();

  const tFin = performance.now ? performance.now() : Date.now();
  const tiempoMs = (tFin - tInicio).toFixed(4);

  return {
    archivo: filepath,
    lineas: contenido.split('\n').length,
    tokens: tokens.length,
    errores: parser.errores,
    warnings: parser.warnings,
    ast,
    tiempo_ms: parseFloat(tiempoMs),
    estado: parser.errores.length === 0 ? 'ACEPTADO' : 'RECHAZADO'
  };
}

// ─────────────────────────────────────────────────────────────
// 6. CLI
// ─────────────────────────────────────────────────────────────
const archivos = process.argv.slice(2).length > 0 ? process.argv.slice(2) : ['docker-compose.yml'];

for (const archivo of archivos) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(` Parser Node.js → ${archivo}`);
  console.log('='.repeat(60));

  const resultado = analizarCompose(archivo);
  if (resultado.error) {
    console.log(`  ❌ ${resultado.error}`);
    continue;
  }

  console.log(`  Líneas      : ${resultado.lineas}`);
  console.log(`  Tokens      : ${resultado.tokens}`);
  console.log(`  Errores     : ${resultado.errores.length}`);
  console.log(`  Warnings    : ${resultado.warnings.length}`);
  console.log(`  Tiempo      : ${resultado.tiempo_ms} ms`);
  console.log(`  Estado      : ${resultado.estado}`);

  if (resultado.errores.length > 0) {
    console.log('\n  Errores encontrados:');
    resultado.errores.forEach(e => console.log(`    ⚠ ${e}`));
  }

  console.log(`\n  AST generado:\n${imprimirAST(resultado.ast)}`);
}
