#include <string>
#include <iostream>
// n = 3

// {{{}}} {}{}{} {{}{}}

using namespace std;

void bracket_combinations(size_t n, size_t open = 0, size_t close = 0, string s = {}){
    if (open == n && close == n) {
        cerr << s << endl;
        return;
    }


    if(open < n ) bracket_combinations(n, open + 1, close, s + "{");

    if(close < open) bracket_combinations(n, open, close + 1, s + "}");
}


int main()
{

    bracket_combinations(5);
    return 0;
}