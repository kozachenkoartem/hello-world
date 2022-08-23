g++-11 -fsanitize=address -static-libasan -std=c++20  "$1"  -lboost_program_options  -o test 
