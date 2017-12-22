#include "prime_numbers_generator.h"
namespace prime_numbers{

bool prime_numbers_generator::m_is_prime(long n)
{
    if(n < 4) return true;
    long int i(2);
    long int k(1);
    if(!(n % i++)){return false;} // 2
    if(!(n % i)){return false;} // 3
    while(i * i < n)
    {
        i = 6 * k - 1;
        if(!(n % i))return false;
        i = 6 * k + 1;
        if(!(n % i))return false;
        k++;
    }
    return true;
}

long prime_numbers_generator::get_next_prime()
{
    if(n <= 3) return n++;
    do
    {
        n = 6 * k + d;
        d = d * -1;
        if(d < 0)k++;
    }while(!m_is_prime(n));
    return n;
}

}//namespace prime_numbers
