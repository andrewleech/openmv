/*
 * This file is part of the OpenMV project.
 * Copyright (c) 2013/2014 Ibrahim Abdelkader <i.abdalkader@gmail.com>
 * This work is licensed under the MIT license, see the file LICENSE for details.
 *
 * module stubs when compiling for unix port.
 *
 */
#include <math.h>
#include <string.h>
#include "py/runtime.h"
#include "py/gc.h"
#include "py_helper.h"
#include "framebuffer.h"
#include "imlib.h"

#define MODULE_UNAVAILABLE(mod) \
static const mp_map_elem_t mod ## _globals_dict_table[] = { \
    { MP_OBJ_NEW_QSTR(MP_QSTR___name__),    MP_OBJ_NEW_QSTR(MP_QSTR_ ## mod)  }, \
    { MP_OBJ_NEW_QSTR(MP_QSTR___init__),    (mp_obj_t)&py_func_unavailable_obj    }, \
}; \
MP_DEFINE_CONST_DICT(mod ## _globals_dict, mod ## _globals_dict_table); \
const mp_obj_module_t mod ## _module = { \
    .base = { &mp_type_module }, \
    .globals = (mp_obj_t)&mod ## _globals_dict, \
};

MODULE_UNAVAILABLE(cpufreq);
MODULE_UNAVAILABLE(fir);
MODULE_UNAVAILABLE(nn);
MODULE_UNAVAILABLE(lcd);
MODULE_UNAVAILABLE(sensor);

// Framebuffer implementation for Unix port using official framebuffer.c

// Memory layout for Unix port:
// All OpenMV memory regions must be contiguous for fb_alloc to work correctly.
// We use a single struct to ensure proper layout and alignment.

#define OMV_FB_MEMORY_SIZE (1024 * 1024)    // 1MB main framebuffer
#define OMV_SB_MEMORY_SIZE (512 * 1024)     // 512KB streaming buffer
#define OMV_FB_ALLOC_SIZE (2 * 1024 * 1024) // 2MB fb_alloc temp buffer

// Macro stringification helper for asm
#define STR(x) STR2(x)
#define STR2(x) #x

// Static buffer allocation for Unix port
// IMPORTANT: fb_alloc.c does pointer arithmetic between framebuffer and fb_alloc regions,
// so they MUST be contiguous in memory. We use a struct to guarantee this.

struct __attribute__((aligned(32))) {
    char fb_memory[OMV_FB_MEMORY_SIZE];      // Main framebuffer
    char sb_memory[OMV_SB_MEMORY_SIZE];      // Streaming buffer
    char fb_alloc_memory[OMV_FB_ALLOC_SIZE]; // fb_alloc temp buffer
} omv_memory_region = {0};

// Provide symbols expected by framebuffer.c
char *_fb_memory_start = omv_memory_region.fb_memory;
char *_fb_memory_end = omv_memory_region.fb_memory + OMV_FB_MEMORY_SIZE;

char *_sb_memory_start = omv_memory_region.sb_memory;
char *_sb_memory_end = omv_memory_region.sb_memory + OMV_SB_MEMORY_SIZE;

// Provide symbol expected by common/fb_alloc.c (Unix version uses pointer)
char *_fb_alloc_end_ptr = omv_memory_region.fb_alloc_memory + OMV_FB_ALLOC_SIZE;

// Note: framebuffer_update_preview() is provided by framebuffer.c
// It returns early if streaming buffer is disabled, so no override needed
// Note: fb_alloc functions are provided by common/fb_alloc.c

// Fast math stubs - only include functions not already defined as macros
// Our fmath.h defines most as macros, but some files don't include it

#ifndef fast_atan2f
float fast_atan2f(float y, float x) {
    return atan2f(y, x);
}
#endif

#ifndef fast_log
float fast_log(float x) {
    return logf(x);
}
#endif

#ifndef fast_expf
float fast_expf(float x) {
    return expf(x);
}
#endif

#ifndef fast_cbrtf
float fast_cbrtf(float x) {
    return cbrtf(x);
}
#endif

// Unaligned memory copy - on Unix we can just use memcpy
void unaligned_memcpy(void *dst, const void *src, size_t n) {
    memcpy(dst, src, n);
}

// Initialize framebuffer and fb_alloc subsystems for Unix port
// This is called automatically at library load time using GCC constructor attribute
__attribute__((constructor))
static void omv_unix_init(void) {
    extern void fb_alloc_init0(void);
    extern void framebuffer_init0(void);

    fb_alloc_init0();
    framebuffer_init0();
}

// Note: m_free is provided by MicroPython's py/malloc.c when MICROPY_MALLOC_USES_ALLOCATED_SIZE=0

// Additional fast math function
#ifndef fast_atanf
float fast_atanf(float x) {
    return atanf(x);
}
#endif
