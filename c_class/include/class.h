#ifndef CLASS_H_
#define CLASS_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct class_ifc_s* class_ifc;

struct class_ifc_s {
    void (*destroy)(const class_ifc* _this);
    uint32_t (*get_a)(const class_ifc* _this);
    uint32_t (*get_b)(const class_ifc* _this);
    void (*set_a)(const class_ifc* _this, uint32_t val);
    void (*set_b)(const class_ifc* _this, uint32_t val);
};

bool class_create(const class_ifc** ifc);

#ifdef __cplusplus
} // extern "C" {
#endif

#endif /* CLASS_H_ */
