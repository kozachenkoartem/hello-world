#include "class.h"
#include <stddef.h>
#include <stdlib.h>

#ifndef containerof
#define containerof(ptr, type, member) ((type*)((uintptr_t)(ptr)-offsetof(type, member)))
#endif

typedef struct {
    class_ifc p_ifc;
    uint32_t a;
    uint32_t b;
} class_impl_t;


void destroy(const class_ifc* _this){

    class_impl_t* impl = containerof(_this, class_impl_t, p_ifc);
    free((void*)impl);
}

uint32_t get_a(const class_ifc* _this){
    class_impl_t* impl = containerof(_this, class_impl_t, p_ifc);
    return impl->a;
}

uint32_t get_b(const class_ifc* _this){
    class_impl_t* impl = containerof(_this, class_impl_t, p_ifc);
    return impl->b;
}

void set_a(const class_ifc* _this, uint32_t val){
    class_impl_t* impl = containerof(_this, class_impl_t, p_ifc);
    impl->a = val;
}

void set_b(const class_ifc* _this, uint32_t val){
    class_impl_t* impl = containerof(_this, class_impl_t, p_ifc);
    impl->b = val;
}

static struct class_ifc_s v_table = {
    .destroy = destroy,
    .get_a = get_a,
    .get_b = get_b,
    .set_a = set_a,
    .set_b = set_b,
};

bool class_create(const class_ifc **ifc)
{
    class_impl_t* impl = (class_impl_t*)calloc(1, sizeof (class_impl_t));
    if(!impl){
        return false;
    }

    impl->p_ifc = &v_table;
    *ifc = &(impl->p_ifc);

    return true;
}
