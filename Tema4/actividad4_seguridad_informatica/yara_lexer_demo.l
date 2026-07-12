%{
/*
 * Prototipo Demostrativo de Analizador Léxico para Reglas YARA (Ciberseguridad)
 * Construido con el Metacompilador FLEX
 * Universidad Nacional Experimental de Guayana (UNEG) - Tema 4
 */
#include <stdio.h>
#include <stdlib.h>

int yara_line = 1;
%}

%option noyywrap

DIGITO          [0-9]
HEX_BYTE        ([0-9a-fA-F]{2}|\?\?)
IDENTIFICADOR   [a-zA-Z_][a-zA-Z0-9_]*
STRING_VAR      \${IDENTIFICADOR}

%%

"//".*          { /* Ignorar comentarios de una línea */ }
"/*"([^*]|\*+[^*/])*\*+"/" { /* Ignorar comentarios multilínea */ }
[ \t\r]+        { /* Ignorar espacios */ }
\n              { yara_line++; }

 /* Palabras Clave Estructurales de YARA */
"rule"          { printf("TOKEN: YARA_RULE_KW | Lexema: %s | Línea: %d\n", yytext, yara_line); }
"meta:"         { printf("TOKEN: YARA_META_SECTION | Lexema: %s | Línea: %d\n", yytext, yara_line); }
"strings:"      { printf("TOKEN: YARA_STRINGS_SECTION | Lexema: %s | Línea: %d\n", yytext, yara_line); }
"condition:"    { printf("TOKEN: YARA_CONDITION_SECTION | Lexema: %s | Línea: %d\n", yytext, yara_line); }

 /* Modificadores de Cadena */
"ascii"|"wide"|"nocase"|"fullword" {
    printf("TOKEN: YARA_STRING_MODIFIER | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Operadores Lógicos y Específicos de YARA */
"or"|"and"|"not"|"at"|"in"|"contains"|"filesize" {
    printf("TOKEN: YARA_OPERATOR | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Variables de Cadena (ej. $firma_malware) */
{STRING_VAR} {
    printf("TOKEN: YARA_STRING_VARIABLE | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Patrones Hexadecimales de Búsqueda de Malware (ej. { E8 ?? ?? 8B 45 }) */
\{({HEX_BYTE}|[ \t\n\r])+\} {
    printf("TOKEN: YARA_HEX_SIGNATURE | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Literales de Texto y Números */
\"([^\"\\]|\\.)*\" {
    printf("TOKEN: YARA_TEXT_LITERAL | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

{DIGITO}+(KB|MB)? {
    printf("TOKEN: YARA_SIZE_OR_NUMBER | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Identificadores Generales (Nombres de Reglas, variables de meta) */
{IDENTIFICADOR} {
    printf("TOKEN: YARA_IDENTIFIER | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

 /* Operadores sintácticos comunes */
[={}()<>,.*+-] {
    printf("TOKEN: YARA_DELIMITER | Lexema: %s | Línea: %d\n", yytext, yara_line);
}

. {
    printf("ERROR LÉXICO YARA: Símbolo desconocido '%s' en Línea %d\n", yytext, yara_line);
}

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *f = fopen(argv[1], "r");
        if (!f) {
            perror("Error al abrir archivo de regla YARA");
            return 1;
        }
        yyin = f;
        printf("=== ANÁLISIS LÉXICO DE REGLA YARA (FLEX DEMO) ===\n");
        yylex();
        fclose(f);
    } else {
        printf("Uso: ./yara_lexer_demo <archivo_regla.yara>\n");
    }
    return 0;
}
