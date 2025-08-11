#include "xpath_lexer.h"
#include <cstring>
#include <string>

XPathLexer::XPathLexer(const char* input, size_t size)
    : cur(input), end(input + size), start(nullptr) {}

Token XPathLexer::nextToken() {
    start = cur;
    const char *marker;  // Объявляем marker перед re2c блоком

    /*!re2c
    re2c:define:YYCTYPE = char;
    re2c:define:YYCURSOR = cur;
    re2c:define:YYLIMIT = end;
    re2c:define:YYMARKER = marker;
    re2c:yyfill:enable = 0;
    re2c:eof = 0;

    // Шаблоны
    digit = [0-9];
    name_start = [a-zA-Z_\x80-\xFF];
    name_char = name_start | [-.0-9];
    single_quote = "'";
    double_quote = '"';

    // Обработка ошибок
    * { return {TokenType::TOK_UNEXPECTED_CHAR, start, 1}; }
    $ { return {TokenType::TOK_EOF, nullptr, 0}; }

    // Пропуск пробельных символов
    [ \t\r\n]+ { return nextToken(); }

    // Числа
    digit+ {
        return {TokenType::TOK_INTEGER, start, static_cast<size_t>(cur - start)};
    }
    (digit+ '.' digit*) | ('.' digit+) {
        return {TokenType::TOK_DECIMAL, start, static_cast<size_t>(cur - start)};
    }

    // Строки
    single_quote [^\']* single_quote {
        return {TokenType::TOK_STRING, start+1, static_cast<size_t>(cur - start - 2)};
    }
    double_quote [^\"]* double_quote {
        return {TokenType::TOK_STRING, start+1, static_cast<size_t>(cur - start - 2)};
    }
    (single_quote [^\']*) | (double_quote [^\"\n]*) {
        return {TokenType::TOK_UNCLOSED_STRING, start, static_cast<size_t>(cur - start)};
    }

    // Переменные и имена
    '$' name_start name_char* {
        return {TokenType::TOK_VARIABLE, start+1, static_cast<size_t>(cur - start - 1)};
    }
    name_start name_char* {
        // Проверка ключевых слов
        size_t len = cur - start;
        if(len == 3) {
            if(strncmp(start, "and", 3) == 0) return {TokenType::TOK_AND, start, len};
            if(strncmp(start, "mod", 3) == 0) return {TokenType::TOK_MOD, start, len};
            if(strncmp(start, "div", 3) == 0) return {TokenType::TOK_DIV, start, len};
        }
        if(len == 2) {
            if(strncmp(start, "or", 2) == 0) return {TokenType::TOK_OR, start, len};
        }
        if(len == 4) {
            if(strncmp(start, "text", 4) == 0) return {TokenType::TOK_TEXT, start, len};
            if(strncmp(start, "node", 4) == 0) return {TokenType::TOK_NODE, start, len};
        }
        if(len == 7) {
            if(strncmp(start, "comment", 7) == 0) return {TokenType::TOK_COMMENT, start, len};
        }
        if(len == 2 && strncmp(start, "pi", 2) == 0) {
            return {TokenType::TOK_PI, start, len};
        }
        return {TokenType::TOK_NAME, start, static_cast<size_t>(cur - start)};
    }

    // Операторы
    "+" { return {TokenType::TOK_PLUS, start, 1}; }
    "-" { return {TokenType::TOK_MINUS, start, 1}; }
    "*" { return {TokenType::TOK_MULT, start, 1}; }
    "=" { return {TokenType::TOK_EQ, start, 1}; }
    "!=" { return {TokenType::TOK_NE, start, 2}; }
    "<" { return {TokenType::TOK_LT, start, 1}; }
    "<=" { return {TokenType::TOK_LE, start, 2}; }
    ">" { return {TokenType::TOK_GT, start, 1}; }
    ">=" { return {TokenType::TOK_GE, start, 2}; }

    // Навигация
    "." { return {TokenType::TOK_DOT, start, 1}; }
    ".." { return {TokenType::TOK_DDOT, start, 2}; }
    "@" { return {TokenType::TOK_AT, start, 1}; }
    "::" { return {TokenType::TOK_COLON2, start, 2}; }
    "/" { return {TokenType::TOK_SLASH, start, 1}; }
    "//" { return {TokenType::TOK_DSLASH, start, 2}; }
    "[" { return {TokenType::TOK_LBRACKET, start, 1}; }
    "]" { return {TokenType::TOK_RBRACKET, start, 1}; }

    // Специальные
    "(" { return {TokenType::TOK_LPAREN, start, 1}; }
    ")" { return {TokenType::TOK_RPAREN, start, 1}; }
    "," { return {TokenType::TOK_COMMA, start, 1}; }
    */
}