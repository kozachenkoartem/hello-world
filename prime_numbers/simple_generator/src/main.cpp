#include <iostream>
#include "prime_numbers_generator.h"


int main()
{
    prime_numbers::prime_numbers_generator g;

    for(auto i = 0; i < 10000; i++)
    {
        std::cerr << g.get_next_prime() << std::endl;
    }
    return 0;

}
