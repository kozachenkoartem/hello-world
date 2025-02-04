#include <vector>
#include <string>
#include <iostream>

constexpr auto my_const = 123;

class my_class {
    int value;
    std::vector<std::string> strs;

public:
    void setValue(int v)
    {
        value = v;
    }

    void GetValue(int v)
    {
        return value;
    }

    void setVector(std::vector<std::string> s)
    {
        strs = s;
    }

    void PrintStrs() {
        for(auto str : strs) {
            std::cerr << " srt: " << str << std::endl;
        }
    }
};


struct my_struct
{
    int value_
    int count_
};