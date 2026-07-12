%{
/*
 * Analizador Léxico para "MiniRust" (Subconjunto del Lenguaje Rust)
 * Construido con el Metacompilador FLEX
 * Universidad Nacional Experimental de Guayana (UNEG) - Tema 4
 *
 * Módulo C de encabezados y variables globales para seguimiento de línea y columna.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int line_num = 1;
int col_num = 1;

/* Función auxiliar para imprimir tokens con formato uniforme */
void print_token(const char* token_type, const char* lexema) {
    printf("%-18s | %-32s | Lnea: %-4d | Columna: %-4d\n", token_type, lexema, line_num, col_num);
    col_num += strlen(lexema);
}
%}

%option noyywrap
%option yylineno

/* Definiciones de expresiones regulares base (macros en Flex) */
DIGITO          [0-9]
LETRA           [a-zA-Z_]
IDENTIFICADOR   {LETRA}({LETRA}|{DIGITO})*
ENTERO          {DIGITO}+
FLOTANTE        {DIGITO}+\.{DIGITO}+
CADENA          \"([^\"\\]|\\.)*\"
COMENTARIO_LINE //.*

%%

 /* -------------------------------------------------------------------------
  * 1. COMENTARIOS Y ESPACIOS EN BLANCO
  * ------------------------------------------------------------------------- */
{COMENTARIO_LINE} {
    /* Ignorar comentario de una línea pero avanzar la columna */
    col_num += yyleng;
}

"/*"([^*]|\*+[^*/])*\*+"/" {
    /* Ignorar comentarios multilínea de bloque y actualizar líneas/columnas */
    for(int i = 0; i < yyleng; i++) {
        if(yytext[i] == '\n') {
            line_num++;
            col_num = 1;
        } else {
            col_num++;
        }
    }
}

\n {
    line_num++;
    col_num = 1;
}

[ \t\r]+ {
    col_num += yyleng;
}

 /* -------------------------------------------------------------------------
  * 2. PALABRAS CLAVE DEL SUBCONJUNTO DE RUST (KEYWORDS & TIPOS)
  * ------------------------------------------------------------------------- */
"fn"            { print_token("TK_KEYWORD_FN", yytext); }
"let"           { print_token("TK_KEYWORD_LET", yytext); }
"mut"           { print_token("TK_KEYWORD_MUT", yytext); }
"if"            { print_token("TK_KEYWORD_IF", yytext); }
"else"          { print_token("TK_KEYWORD_ELSE", yytext); }
"while"         { print_token("TK_KEYWORD_WHILE", yytext); }
"for"           { print_token("TK_KEYWORD_FOR", yytext); }
"in"            { print_token("TK_KEYWORD_IN", yytext); }
"return"        { print_token("TK_KEYWORD_RETURN", yytext); }
"true"          { print_token("TK_BOOL_TRUE", yytext); }
"false"         { print_token("TK_BOOL_FALSE", yytext); }
"println!"      { print_token("TK_MACRO_PRINTLN", yytext); }

"i32"           { print_token("TK_TYPE_I32", yytext); }
"f64"           { print_token("TK_TYPE_F64", yytext); }
"bool"          { print_token("TK_TYPE_BOOL", yytext); }
"char"          { print_token("TK_TYPE_CHAR", yytext); }
"String"        { print_token("TK_TYPE_STRING", yytext); }

 /* -------------------------------------------------------------------------
  * 3. OPERADORES MULTICARÁCTER Y RELACIONALES
  * ------------------------------------------------------------------------- */
"=="            { print_token("TK_OP_EQ", yytext); }
"!="            { print_token("TK_OP_NEQ", yytext); }
"<="            { print_token("TK_OP_LTE", yytext); }
">="            { print_token("TK_OP_GTE", yytext); }
"&&"            { print_token("TK_OP_AND", yytext); }
"||"            { print_token("TK_OP_OR", yytext); }
"->"            { print_token("TK_OP_ARROW", yytext); }
".."            { print_token("TK_OP_RANGE", yytext); }
"+="            { print_token("TK_OP_ADD_ASSIGN", yytext); }
"-="            { print_token("TK_OP_SUB_ASSIGN", yytext); }

 /* -------------------------------------------------------------------------
  * 4. OPERADORES ARITMÉTICOS Y DE ASIGNACIÓN
  * ------------------------------------------------------------------------- */
"+"             { print_token("TK_OP_ADD", yytext); }
"-"             { print_token("TK_OP_SUB", yytext); }
"*"             { print_token("TK_OP_MUL", yytext); }
"/"             { print_token("TK_OP_DIV", yytext); }
"%"             { print_token("TK_OP_MOD", yytext); }
"="             { print_token("TK_OP_ASSIGN", yytext); }
"<"             { print_token("TK_OP_LT", yytext); }
">"             { print_token("TK_OP_GT", yytext); }
"!"             { print_token("TK_OP_NOT", yytext); }
"&"             { print_token("TK_OP_REF", yytext); }

 /* -------------------------------------------------------------------------
  * 5. DELIMITADORES Y PUNTUACIÓN SINTÁCTICA
  * ------------------------------------------------------------------------- */
"("             { print_token("TK_LPAREN", yytext); }
")"             { print_token("TK_RPAREN", yytext); }
"{"             { print_token("TK_LBRACE", yytext); }
"}"             { print_token("TK_RBRACE", yytext); }
"["             { print_token("TK_LBRACKET", yytext); }
"]"             { print_token("TK_RBRACKET", yytext); }
":"             { print_token("TK_COLON", yytext); }
";"             { print_token("TK_SEMICOLON", yytext); }
","             { print_token("TK_COMMA", yytext); }
"."             { print_token("TK_DOT", yytext); }

 /* -------------------------------------------------------------------------
  * 6. IDENTIFICADORES Y LITERALES NUMÉRICOS / CADENAS
  * ------------------------------------------------------------------------- */
{IDENTIFICADOR} { print_token("TK_IDENTIFICADOR", yytext); }
{FLOTANTE}      { print_token("TK_LIT_FLOAT", yytext); }
{ENTERO}        { print_token("TK_LIT_INT", yytext); }
{CADENA}        { print_token("TK_LIT_STRING", yytext); }

 /* -------------------------------------------------------------------------
  * 7. MANEJO DE ERRORES LÉXICOS (MISMATCH / CARACTERES NO RECONOCIDOS)
  * ------------------------------------------------------------------------- */
. {
    printf("\n[!] ERROR LXICO CRITICO: Caracter no reconocido '%s' en Lnea %d, Columna %d\n\n", yytext, line_num, col_num);
    col_num += yyleng;
}

%%

/* -------------------------------------------------------------------------
 * SECCIÓN DE CÓDIGO DE USUARIO EN C (FUNCIÓN MAIN)
 * ------------------------------------------------------------------------- */
int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *file = fopen(argv[1], "r");
        if (!file) {
            perror("Error fatal al abrir el archivo de entrada");
            return 1;
        }
        yyin = file;
        printf("==============================================================================\n");
        printf(" ANÁLISIS LÉXICO MINIRUST (FLEX) - Archivo: %s\n", argv[1]);
        printf("==============================================================================\n");
        printf("%-18s | %-32s | %-10s | %-10s\n", "TIPO DE TOKEN", "LEXEMA (VALOR)", "LÍNEA", "COLUMNA");
        printf("------------------------------------------------------------------------------\n");
        yylex();
        printf("==============================================================================\n");
        fclose(file);
    } else {
        printf("Uso: ./analizador_rust <archivo_fuente.rs>\n");
        printf("Ingresando en modo interactivo (escriba código MiniRust y presione Ctrl+D / Ctrl+Z):\n");
        yylex();
    }
    return 0;
}
