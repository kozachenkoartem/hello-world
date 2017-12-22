cmake_minimum_required(VERSION 2.8)
project(prime_numbers)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall")

set(ALL_SOURCE_FILES
    ${CMAKE_SOURCE_DIR}/src/prime_numbers_generator.h
    ${CMAKE_SOURCE_DIR}/src/prime_numbers_generator.cpp
    ${CMAKE_SOURCE_DIR}/src/main.cpp
)

add_executable(prime_numbers ${ALL_SOURCE_FILES})


