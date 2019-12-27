#include <gtest/gtest.h>
#include "lib.h"


class TestLib: public ::testing::Test {};

TEST_F(TestLib, test_func) {
    ASSERT_EQ(func(3, 4), 12);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
