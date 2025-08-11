cmake_minimum_required(VERSION 3.10)
project(xpath_lexer)

# Настройки компилятора
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Поиск re2c
find_program(RE2C_EXECUTABLE re2c)
if(NOT RE2C_EXECUTABLE)
    message(FATAL_ERROR "re2c not found! Install with: sudo apt install re2c")
endif()

# Генерация лексера
set(LEXER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/src/xpath_lexer.re)
set(LEXER_OUT ${CMAKE_CURRENT_BINARY_DIR}/xpath_lexer.cpp)


# Подавляем специфические предупреждения re2c
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wno-useless-escape)
endif()

add_custom_command(
    OUTPUT ${LEXER_OUT}
    COMMAND ${RE2C_EXECUTABLE} -W -o ${LEXER_OUT} ${LEXER_SRC}
    DEPENDS ${LEXER_SRC}
    COMMENT "Generating lexer with re2c"
)

# Исполняемый файл
add_executable(xpath_lexer
    src/main.cpp
    ${LEXER_OUT}
)

# Пути к заголовкам
target_include_directories(xpath_lexer PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Установка для генерации IDE-проектов
set_source_files_properties(${LEXER_OUT} PROPERTIES GENERATED TRUE)