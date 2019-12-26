set (CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address -fsanitize=null")
set (CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -fno-omit-frame-pointer -fsanitize=address -fsanitize=null")

SET(TEST_LIST_COV)

FILE(GLOB_RECURSE TEST_SOURCES "test_*.cpp")
FOREACH(TEST_SOURCE ${TEST_SOURCES})
    GET_FILENAME_COMPONENT(test_name ${TEST_SOURCE} NAME_WE)
    ADD_EXECUTABLE(${test_name} ${TEST_SOURCE} utils.cpp)
    TARGET_LINK_LIBRARIES(${test_name} lib gtest)
    ADD_TEST(${test_name} ${test_name} "--gtest_output=xml:${test_name}.xml")
    SET(TEST_LIST_COV ${TEST_LIST_COV} ${test_name})
ENDFOREACH()

FILE(GLOB_RECURSE TEST_SOURCES "test_*.c")
FOREACH(TEST_SOURCE ${TEST_SOURCES})
    GET_FILENAME_COMPONENT(test_name ${TEST_SOURCE} NAME_WE)
    ADD_EXECUTABLE(${test_name} ${TEST_SOURCE})
    TARGET_LINK_LIBRARIES(${test_name} lib unity)
    ADD_TEST(${test_name} bash -eco pipefail -c "./${test_name} | tee ${test_name}.test")
    SET(TEST_LIST_COV ${TEST_LIST_COV} ${test_name})
ENDFOREACH()

IF(ENABLE_COVERAGE)
    SETUP_TARGET_FOR_COVERAGE_LCOV(
            NAME coverage
            EXECUTABLE ctest -j ${n_cores} # Executable in PROJECT_BINARY_DIR
            DEPENDENCIES
                ${TEST_LIST_COV})
ENDIF()
