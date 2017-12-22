#pragma once
#ifndef PRIME_NUMBERS_GENERATOR_H
#define PRIME_NUMBERS_GENERATOR_H

namespace prime_numbers{

class prime_numbers_generator
{
    int k = {1};
    int n = {1};
    int d = {-1};
    bool m_is_prime(long int n);
public:
    long int get_next_prime();
};

}//namespace prime_numbers

#endif // PRIME_NUMBERS_GENERATOR_H
