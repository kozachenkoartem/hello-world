#include <unity.h>
#include "class.h"

void setUp(void) {

}

void tearDown(void) {

}

void class_test(void) {

    const class_ifc *cls = NULL;

    TEST_ASSERT_EQUAL(class_create(&cls), true);
    TEST_ASSERT_NOT_NULL(cls);

    TEST_ASSERT_EQUAL((*cls)->get_a(cls), 0);
    TEST_ASSERT_EQUAL((*cls)->get_b(cls), 0);

    (*cls)->set_a(cls, 444);
    (*cls)->set_b(cls, 555);

    TEST_ASSERT_EQUAL((*cls)->get_a(cls), 444);
    TEST_ASSERT_EQUAL((*cls)->get_b(cls), 555);

    (*cls)->destroy(cls);
}

int main(int argc, char** argv) {
    UNITY_BEGIN();
    RUN_TEST(class_test);
    return UNITY_END();
}
