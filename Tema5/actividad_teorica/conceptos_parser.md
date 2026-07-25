# Actividad Teórica – Tema 5: Análisis Sintáctico

---

## Pregunta 1: Árbol de Sintaxis Abstracta (AST)

### ¿Qué es un AST?

Un **Árbol de Sintaxis Abstracta** (Abstract Syntax Tree, **AST**) es una representación en forma de árbol de la **estructura lógica y semántica** de un programa. A diferencia del Árbol de Análisis Sintáctico Concreto (CST o *parse tree*), el AST **elimina los nodos que no aportan información semántica** (paréntesis, comas de separación, palabras clave estructurales redundantes), conservando únicamente los elementos con significado computacional.

### Diferencias AST vs. CST (Árbol de Derivación Concreto)

| Característica | CST (Árbol Concreto) | AST (Árbol Abstracto) |
|---|---|---|
| **Nodos** | Uno por cada símbolo de la gramática | Solo nodos con significado semántico |
| **Terminales** | Incluye todos (paréntesis, comas, etc.) | Omite los que no aportan semántica |
| **Tamaño** | Mayor (más verboso) | Más compacto y eficiente |
| **Uso** | Verificación gramatical pura | Base para análisis semántico y generación de código |

### Ejemplo Práctico en Python

**Código fuente de entrada:**
```python
resultado = (3 + 5) * 2
```

**AST resultante (visualizado):**
```
     Asignación
     /         \
"resultado"    Multiplicación
               /              \
            Suma               2
           /    \
          3      5
```

**Representación como diccionario Python (estructura real del nodo):**
```python
ast = {
    "tipo": "Asignacion",
    "identificador": "resultado",
    "valor": {
        "tipo": "BinOp",
        "operador": "*",
        "izquierdo": {
            "tipo": "BinOp",
            "operador": "+",
            "izquierdo": {"tipo": "Numero", "valor": 3},
            "derecho":  {"tipo": "Numero", "valor": 5}
        },
        "derecho": {"tipo": "Numero", "valor": 2}
    }
}
```

**¿Por qué es fundamental el AST?**
- El compilador usa el AST para la **verificación de tipos** (¿puedo sumar un `int` con un `string`?).
- El **optimizador** puede plegar constantes directamente sobre el AST (ej.: `3 + 5` → `8` antes de generar código).
- Los **generadores de código** recorren el AST en post-orden para emitir instrucciones de bajo nivel (bytecode, código máquina, o código en otro lenguaje).

---

## Pregunta 2: Análisis LL vs. LR — Comparativa Profunda

### Análisis LL (Left-to-right, Leftmost derivation) — Descendente

El parser **LL** procesa la entrada de **izquierda a derecha** y construye la derivación más a la **izquierda** del árbol (top-down). El número entre paréntesis (ej. `LL(1)`) indica cuántos tokens de **lookahead** (anticipación) consulta para tomar cada decisión.

**Algoritmo básico LL(1):**
1. Se mantiene una **pila de símbolos** que comienza con el símbolo inicial.
2. Se consulta el token actual de la entrada (lookahead).
3. Se busca en la **Tabla de Análisis LL** qué producción aplicar.
4. Se reemplaza el tope de la pila por el lado derecho de la producción.
5. Si el tope es un terminal que coincide con la entrada, se hace `pop` y se avanza.
6. Si la pila queda vacía y la entrada también, la cadena es **aceptada**.

**Ventajas:**
- Simple de implementar **manualmente** (Parsers Recursivos Descendentes).
- Mensajes de error claros y precisos.
- Facilidad de depuración.

**Desventajas:**
- No puede manejar gramáticas con **recursión a izquierda** (requiere transformación de la gramática).
- No puede manejar **ambigüedades** directas.
- Limitado a gramáticas LL(k).

---

### Análisis LR (Left-to-right, Rightmost derivation) — Ascendente

El parser **LR** también lee la entrada de izquierda a derecha, pero construye la derivación más a la **derecha** en orden inverso (bottom-up). Usa una técnica **Shift-Reduce**:

- **SHIFT:** Apila el próximo token de la entrada.
- **REDUCE:** Cuando la pila contiene el lado derecho de una producción, la reemplaza por el no terminal del lado izquierdo.

**Variantes de LR:**

| Variante | Lookahead | Potencia | Herramientas |
|---|---|---|---|
| **SLR(1)** | 1 (Follow sets simples) | Menor | Bison (modo básico) |
| **LALR(1)** | 1 (Look-Ahead LR) | Media | Bison/Yacc, ANTLR |
| **CLR(1) o LR(1) canónico** | 1 (conjuntos de items LR(1) completos) | Mayor | GCC (internamente) |

**Ventajas:**
- Maneja **más gramáticas** que LL (incluyendo recursión a izquierda).
- Los generadores automáticos (Bison, ANTLR) simplifican enormemente su construcción.
- Detecta errores **tan pronto** como sea posible (no los pasa por alto).

**Desventajas:**
- Las tablas de análisis LR pueden ser **enormes** (miles de estados).
- Difícil de implementar **a mano**.
- Los mensajes de error son a veces menos intuitivos que en LL.

---

### Tabla Comparativa Final LL vs. LR

| Criterio | LL(1) | LR(1) / LALR(1) |
|---|---|---|
| **Dirección de construcción** | Top-Down (Descendente) | Bottom-Up (Ascendente) |
| **Recursión izquierda** | ❌ No soportada | ✅ Soportada |
| **Gramáticas aceptadas** | Subconjunto de LLC | Casi todos los LLC determinísticos |
| **Facilidad de implementación manual** | ✅ Alta (Recursivo Descendente) | ❌ Baja (requiere tablas) |
| **Herramientas asociadas** | ANTLR (modo LL), parsers a mano | Bison, Yacc, Menhir |
| **Rendimiento** | O(n) | O(n) |
| **Manejo de errores** | Intuitivo y temprano | Puede ser tardío o críptico |

---

## Pregunta 3: Recuperación de Errores en Parsers

### ¿Qué es la Recuperación de Errores?

Es la capacidad del parser de **continuar el análisis después de encontrar un error sintáctico**, en lugar de abortar inmediatamente. Permite reportar múltiples errores en una sola pasada y proveer mensajes más útiles al programador.

### Estrategias Principales

**1. Modo Pánico (Panic Mode) — La más común**
Al detectar un error, el parser **descarta tokens** de la entrada hasta encontrar un token de sincronización (ej: `;`, `}`, `end`). A partir de ese punto, reanuda el análisis.
- **Ventaja:** Sencillo de implementar.
- **Desventaja:** Puede omitir errores subsecuentes legítimos.

```
Error: Se esperaba ';' pero se encontró 'x' en línea 5.
[PÁNICO] Descartando tokens hasta encontrar ';' o '}' …
[RECUPERADO] Continuando análisis desde línea 6.
```

**2. Inserción/Eliminación de Tokens (Corrección Local)**
El parser intenta **insertar el token faltante** o **eliminar el token inesperado** para que la cadena sea válida:
- Si falta un `;`, lo inserta virtualmente y continúa.
- Si hay un token de más, lo descarta.
- Implementado en compiladores como GCC y Clang.

**3. Producciones de Error (Bison/Yacc)**
El programador de la gramática define explícitamente reglas especiales con el token `error`:
```bison
sentencia : expresion ';'
           | error ';'  { yyerrok; /* recuperar al siguiente ';' */ }
           ;
```

**4. Recuperación por Contexto (ANTLR 4)**
ANTLR 4 implementa un algoritmo avanzado que intenta hasta **3 estrategias** en orden antes de entrar en modo pánico:
1. **Single Token Deletion:** ¿Ignorar el token actual resuelve el problema?
2. **Single Token Insertion:** ¿Insertar el token esperado resuelve el problema?
3. **Sync-and-Return:** Activar el modo pánico con retroceso controlado.

### Importancia práctica

Los compiladores modernos como **GCC**, **Clang** y **Rust** implementan recuperación de errores avanzada que permite reportar 5-10 errores simultáneos en una sola compilación, reduciendo significativamente el ciclo de depuración del programador.

---

## Referencias

- Aho, A., Lam, M., Sethi, R., & Ullman, J. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Addison-Wesley. (Dragon Book)
- Parr, T. (2013). *The Definitive ANTLR 4 Reference*. Pragmatic Bookshelf.
- Grune, D., & Jacobs, C. (2008). *Parsing Techniques: A Practical Guide* (2nd ed.). Springer.
