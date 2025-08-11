#pragma once

#include <cstddef>
#include <string_view>

enum class TokenType {
    TOK_EOF,
    TOK_ERROR,
    TOK_UNEXPECTED_CHAR,
    TOK_UNCLOSED_STRING,

    TOK_INTEGER,
    TOK_DECIMAL,
    TOK_STRING,
    TOK_NAME,
    TOK_VARIABLE,

    TOK_PLUS,
    TOK_MINUS,
    TOK_MULT,
    TOK_DIV,
    TOK_MOD,
    TOK_AND,
    TOK_OR,
    TOK_EQ,
    TOK_NE,
    TOK_LT,
    TOK_LE,
    TOK_GT,
    TOK_GE,

    TOK_DOT,
    TOK_DDOT,
    TOK_AT,
    TOK_COLON2,
    TOK_SLASH,
    TOK_DSLASH,
    TOK_LBRACKET,
    TOK_RBRACKET,

    TOK_LPAREN,
    TOK_RPAREN,
    TOK_COMMA,
    TOK_DOLLAR,

    TOK_NODE,
    TOK_TEXT,
    TOK_COMMENT,
    TOK_PI
};

struct Token {
    TokenType type;
    const char* start;
    size_t length;
};

class XPathLexer {
    const char* cur;
    const char* end;
    const char* start;

public:
    XPathLexer(const char* input, size_t size);
    Token nextToken();
};