#include <unity.h>
#include "lib.h"

void setUp(void) {

}

void tearDown(void) {

}

void func_test(void) {
    TEST_ASSERT_EQUAL(func(3, 4), 12);
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(func_test);
    return UNITY_END();
}
