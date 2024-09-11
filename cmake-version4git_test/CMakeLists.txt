cmake_minimum_required(VERSION 3.28)

PROJECT(test_project)

INCLUDE(3rdparty/version4git/cmake/cmake-version4git.cmake)

add_executable(test
    test.cpp
    test.h
    main.cpp
)

PROJECT_VERSION_FROM_GIT()

message("####################### ${PROJECT_VERSION}")

