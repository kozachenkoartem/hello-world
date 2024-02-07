cmake_minimum_required(VERSION 3.5)

project(stacktrace_test LANGUAGES CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
add_definitions( -D_GLIBCXX_HAVE_STACKTRACE )
add_compile_options(-lstdc++_libbacktrace)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt5Core)

add_executable(stacktrace_test
  main.cpp
)
#target_link_libraries(stacktrace_test backtrace)
