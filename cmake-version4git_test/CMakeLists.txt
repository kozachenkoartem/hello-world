CMAKE_MINIMUM_REQUIRED(VERSION 3.0)

PROJECT(test_project)

INCLUDE(3rdparty/version4git/cmake/cmake-version4git.cmake)

add_executable(test
    test.cpp
    test.h
    main.cpp
)