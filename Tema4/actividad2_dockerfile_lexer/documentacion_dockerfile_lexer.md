# Actividad 2: Analizador Léxico para Archivos Docker (`Dockerfile`) con Expresiones Regulares

---

## 1. Introducción y Descripción del Lenguaje

Un archivo `Dockerfile` es un script de configuración de texto plano que contiene una secuencia de instrucciones (o directivas) y argumentos que el motor de construcción de Docker ejecuta sucesivamente para empaquetar una imagen de contenedor.

Aunque **no se requiere tener el motor de Docker instalado** para ejecutar nuestro analizador léxico (ya que el análisis se realiza exclusivamente sobre la gramática regular del texto), nuestro programa en Python actúa como la **primera fase de un compilador/verificador** (`Lexer`), escaneando el código fuente carácter por carácter y agrupándolos en componentes léxicos (`Tokens`).

---

## 2. Alfabeto y Tabla de Tokens Definidos

Para nuestro analizador léxico (`dockerfile_lexer.py`), hemos estructurado el reconocimiento en los siguientes patrones regulares y componentes léxicos:

| Token (`kind`) | Descripción / Lexema | Expresión Regular (`pattern`) | Ejemplo Real |
| :--- | :--- | :--- | :--- |
| `COMMENT` | Comentarios de una línea (inician con `#`) | `^\s*#.*` | `# Configuración base` |
| `DIRECTIVE` | Palabras clave e instrucciones del Dockerfile | `\b(?:FROM\|RUN\|CMD\|LABEL\|EXPOSE\|ENV\|ADD\|COPY\|ENTRYPOINT\|VOLUME\|USER\|WORKDIR\|ARG\|ONBUILD\|STOPSIGNAL\|HEALTHCHECK\|SHELL)\b` | `FROM`, `RUN`, `COPY` |
| `FLAG` | Opciones y modificadores de directiva | `--[a-zA-Z0-9_-]+(?:=[a-zA-Z0-9_./:-]+)?` | `--platform=linux/amd64`, `--from=builder` |
| `VARIABLE` | Variables de entorno y expansiones | `\$[a-zA-Z_][a-zA-Z0-9_]*\|\$\{[a-zA-Z_][a-zA-Z0-9_]*(?::-[^}]+)?\}` | `$PORT`, `${NODE_ENV}`, `${GO_VERSION}` |
| `STRING` | Cadenas delimitadas por comillas dobles o simples | `"[^"\\]*(?:\\.[^"\\]*)*"\|'[^\'\\]*(?:\\.[^\'\\]*)*'` | `"node"`, `'production'` |
| `OPERATOR` | Operadores y delimitadores sintácticos | `&&\|\|\|\|\|\\\|=\|:\|,\|\[\|\]\|\(\|\)` | `&&`, `=`, `[`, `]` |
| `PORT` | Números de puerto con protocolo de red | `\b\d{1,5}/(?:tcp\|udp)\b` | `8080/tcp`, `3000/udp` |
| `NUMBER` | Valores numéricos enteros | `\b\d+\b` | `80`, `3`, `10` |
| `WORD` | Identificadores, rutas, comandos e imágenes | `[a-zA-Z0-9._-]+(?:/[a-zA-Z0-9._-]+)*(?::[a-zA-Z0-9._-]+)?` | `python:3.11-slim`, `/usr/src/app` |
| `NEWLINE` | Salto de línea (control de línea) | `\n` | `\n` |
| `SKIP` | Espacios en blanco y tabulaciones | `[ \t\r]+` | ` ` *(ignorado)* |
| `MISMATCH` | Carácter o símbolo no válido (Error Léxico) | `.` | `¿`, `¡`, `@@` |

---

## 3. Construcción Paso a Paso en Python (`dockerfile_lexer.py`)

1. **Definición de Patrones Ordenados (`DOCKER_TOKENS`):**
   Utilizamos una lista de tuplas `(nombre_token, regex)` en Python. El orden es crítico: colocamos `PORT` (`8080/tcp`) antes que `NUMBER` (`8080`) y `WORD` para evitar que el analizador divida erróneamente un puerto en un número y una ruta.
2. **Ensamblaje de Expresión Regular con Grupos Nombrados:**
   Se combinan todas las expresiones utilizando el operador de alternancia (`|`) de la sintaxis `(?P<name>pattern)` del módulo `re`.
3. **Iteración Eficiente con `re.finditer`:**
   En lugar de dividir la cadena con `.split()` o hacer múltiples bucles lentos, `re.finditer(input_text, re.MULTILINE | re.IGNORECASE)` recorre el archivo una sola vez desde el inicio hasta el fin (`O(N)`).
4. **Manejo de Posición y Errores (`MISMATCH`):**
   Mantenemos un contador `line_num` y el índice de inicio de línea `line_start`. Cada vez que el motor coincide con `NEWLINE`, incrementamos la línea. Si coincide con `MISMATCH`, calculamos la columna exacta (`mo.start() - line_start + 1`) y lanzamos un `SyntaxError` detallando la línea y el símbolo infractor.

---

## 4. Ejemplos de Ejecución y Pruebas

Hemos incluido 3 archivos de prueba dentro de la carpeta:
* **[Dockerfile_ejemplo1](file:///c:/Users/rafae/Desktop/LYC/Tema4/actividad2_dockerfile_lexer/Dockerfile_ejemplo1)**: Demuestra la tokenización exitosa de una imagen de Node.js básica.
* **[Dockerfile_ejemplo2](file:///c:/Users/rafae/Desktop/LYC/Tema4/actividad2_dockerfile_lexer/Dockerfile_ejemplo2)**: Demuestra directivas complejas (`ARG`, `HEALTHCHECK`, y flags `--from`, `--platform`).
* **[Dockerfile_ejemplo3_errores](file:///c:/Users/rafae/Desktop/LYC/Tema4/actividad2_dockerfile_lexer/Dockerfile_ejemplo3_errores)**: Demuestra cómo el analizador detiene la ejecución al detectar símbolos ilegales (`¿¿error_aqui??`), reportando exactamente:
  ```text
  [!] ERROR LÉXICO en línea 7, columna 28:
      Carácter o secuencia no reconocida: '¿'
      Línea completa: >> RUN pip install -r requirements.txt ¿¿error_aqui?? ¡símbolos_inválidos! <<
  ```

### ¿Cómo ejecutar la demostración en tu consola?
Para probar el analizador en tu computadora sin necesidad de instalar nada más que Python, simplemente abre una terminal o CMD en esta carpeta y ejecuta:
```bash
python run_dockerfile_lexer.py
```
O para analizar un archivo individual en específico:
```bash
python dockerfile_lexer.py Dockerfile_ejemplo1
```
