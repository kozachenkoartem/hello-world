#include "xpath_lexer.h"
#include <iostream>
#include <fstream>
#include <vector>

const char* tokenTypeToString(TokenType type) {
    switch(type) {
        case TokenType::TOK_EOF: return "EOF";
        case TokenType::TOK_ERROR: return "ERROR";
        case TokenType::TOK_UNEXPECTED_CHAR: return "UNEXPECTED_CHAR";
        case TokenType::TOK_UNCLOSED_STRING: return "UNCLOSED_STRING";
        case TokenType::TOK_INTEGER: return "INTEGER";
        case TokenType::TOK_DECIMAL: return "DECIMAL";
        case TokenType::TOK_STRING: return "STRING";
        case TokenType::TOK_NAME: return "NAME";
        case TokenType::TOK_VARIABLE: return "VARIABLE";
        case TokenType::TOK_PLUS: return "PLUS";
        case TokenType::TOK_MINUS: return "MINUS";
        case TokenType::TOK_MULT: return "MULT";
        case TokenType::TOK_DIV: return "DIV";
        case TokenType::TOK_MOD: return "MOD";
        case TokenType::TOK_AND: return "AND";
        case TokenType::TOK_OR: return "OR";
        case TokenType::TOK_EQ: return "EQ";
        case TokenType::TOK_NE: return "NE";
        case TokenType::TOK_LT: return "LT";
        case TokenType::TOK_LE: return "LE";
        case TokenType::TOK_GT: return "GT";
        case TokenType::TOK_GE: return "GE";
        case TokenType::TOK_DOT: return "DOT";
        case TokenType::TOK_DDOT: return "DDOT";
        case TokenType::TOK_AT: return "AT";
        case TokenType::TOK_COLON2: return "COLON2";
        case TokenType::TOK_SLASH: return "SLASH";
        case TokenType::TOK_DSLASH: return "DSLASH";
        case TokenType::TOK_LBRACKET: return "LBRACKET";
        case TokenType::TOK_RBRACKET: return "RBRACKET";
        case TokenType::TOK_LPAREN: return "LPAREN";
        case TokenType::TOK_RPAREN: return "RPAREN";
        case TokenType::TOK_COMMA: return "COMMA";
        case TokenType::TOK_DOLLAR: return "DOLLAR";
        case TokenType::TOK_NODE: return "NODE";
        case TokenType::TOK_TEXT: return "TEXT";
        case TokenType::TOK_COMMENT: return "COMMENT";
        case TokenType::TOK_PI: return "PI";
        default: return "UNKNOWN";
    }
}

void tokenizeAndPrint(const std::string& input) {
    std::cout << "Input: \"" << input << "\"\n";

    XPathLexer lexer(input.data(), input.size());
    Token token;
    int count = 0;

    do {
        token = lexer.nextToken();
        std::cout << "  Token " << ++count << ": "
                  << tokenTypeToString(token.type);

        if(token.start && token.length > 0) {
            std::cout << " -> \"" << std::string_view(token.start, token.length) << "\"";
        }

        std::cout << "\n";

        if(token.type == TokenType::TOK_ERROR ||
           token.type == TokenType::TOK_UNEXPECTED_CHAR ||
           token.type == TokenType::TOK_UNCLOSED_STRING) {
            std::cout << "  [LEXICAL ERROR DETECTED!]\n";
            break;
        }
    } while(token.type != TokenType::TOK_EOF);

    std::cout << "----------------------------------------\n";
}

int main(int argc, char* argv[]) {
    // Примеры для токенизации
    std::vector<std::string> testInputs = {
        "book/title[@lang='en']",
        "/a/b/cbook/title[@lang='en']",
        "/a[b=book/title[@lang='en']]",
        "/a[b=f(book/title[@lang='en'])]",
        "f(/a/bbook/title[@lang='en'])",
        "f(/a/b)='book/title[@lang='en']'",
        "/a[b='book/title[@lang='en']']",
    };

    // Токенизация всех примеров
    for(const auto& input : testInputs) {
        tokenizeAndPrint(input);
    }

    // Токенизация из файла (если указан аргумент)
    if(argc > 1) {
        std::ifstream file(argv[1]);
        if(file) {
            std::string line;
            while(std::getline(file, line)) {
                tokenizeAndPrint(line);
            }
        } else {
            std::cerr << "Error opening file: " << argv[1] << "\n";
        }
    }

    return 0;
}