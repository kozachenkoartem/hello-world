# Example of usage Unity and Google test framworks.

# Build project

## Get sources

Clone project from GitHub into place required by further build,
after clone sources make sure to initialize submodules

```
git submodule update --init --recursive
```

## Building

### Compile with CMake

The basic build version is a debug, to switch use `-DCMAKE_BUILD_TYPE=<build type>`

To build a generic version of the library:

    ```
    mkdir build && cd build
    cmake ../
    make
    ```

#### CMake flags
There is set of CMake flags which can be used:

to use clang compiler

    ```
    cmake ../ -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang
    make -j 12
    ```

to get code coverage report

    ```
    cmake ../ -DCMAKE_BUILD_TYPE=Debug -DENABLE_COVERAGE=ON
    make -j 12
    make coverage
    ```



