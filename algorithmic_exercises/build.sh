g++-11 -fsanitize=address -static-libasan -std=c++20  "$1" -o /tmp/test && /tmp/test
