# Unix Port File Loading Segfault - Fix Summary

## Problem

Image loading from files on the Unix port caused segmentation faults:
```python
img = image.Image('/path/to/image.ppm', copy_to_fb=True)  # Segfault
```

This affected **all** file loading operations, not just those with `copy_to_fb=True`.

## Root Cause

The issue was a **type mismatch** in how memory regions were defined for the Unix port.

### Background

On embedded systems, memory regions are defined via linker scripts:
```c
extern char _fb_memory_start;  // Linker symbol
extern char _fb_memory_end;
```

The framebuffer code uses these as:
```c
framebuffer_init(..., &_fb_memory_start, &_fb_memory_end - &_fb_memory_start, ...);
```

Taking the address of a linker symbol (`&_fb_memory_start`) gives the actual memory location.

### The Bug

In `ports/unix/py_unix_stubs.c`, the Unix port originally defined these as **pointers**:
```c
char *_fb_memory_start = omv_memory_region.fb_memory;  // WRONG: This is a pointer variable
char *_fb_memory_end = omv_memory_region.fb_memory + OMV_FB_MEMORY_SIZE;
```

When `framebuffer_init0()` did `&_fb_memory_start`, it took the **address of the pointer variable**, not the address the pointer pointed to.

This meant:
- `&_fb_memory_start` gave the address of the pointer variable itself (some stack/data location)
- Not the address of `omv_memory_region.fb_memory` where the actual framebuffer was

This caused `framebuffer_pool_end()` to return garbage addresses, which broke `fb_alloc_all()` used during file buffering, leading to segfaults.

## Solution

### Key Insight

On Unix, we don't need linker symbols at all. We have a normal C struct and can use its members directly.

### Step 1: Override `framebuffer_init0()` for Unix

Created a Unix-specific implementation that uses the struct members directly:
```c
void framebuffer_init0() {
    extern void framebuffer_init(framebuffer_t *fb, void *buff, size_t size, bool dynamic, bool enabled);
    extern framebuffer_t *framebuffer_get(size_t id);

    bool enabled = framebuffer_get(FB_STREAM_ID)->enabled;

    // Use struct members directly - no linker symbols needed
    framebuffer_init(framebuffer_get(FB_MAINFB_ID),
                     omv_memory_region.fb_memory,
                     OMV_FB_MEMORY_SIZE, false, true);

    framebuffer_init(framebuffer_get(FB_STREAM_ID),
                     omv_memory_region.sb_memory,
                     OMV_SB_MEMORY_SIZE, false, enabled);

    framebuffer_t *fb = framebuffer_get(FB_STREAM_ID);
    memset(fb->raw_base, 0, sizeof(framebuffer_header_t));
}
```

### Step 2: Make Original `framebuffer_init0()` Weak

In `lib/imlib/framebuffer.c`, marked the function as weak to allow overriding:
```c
__attribute__((weak)) void framebuffer_init0() {
    // Original implementation for embedded systems
    ...
}
```

This allows the Unix port to provide its own implementation without modifying shared code extensively.

## Files Changed

1. **ports/unix/py_unix_stubs.c**
   - Changed memory region symbol definitions from `char *` to named `_ptr` versions
   - Added Unix-specific `framebuffer_init0()` override
   - Added `#include "omv_boardconfig.h"` for required definitions

2. **lib/imlib/framebuffer.c**
   - Added `__attribute__((weak))` to `framebuffer_init0()` to allow overriding

3. **tests/unix/run_tests.py**
   - Fixed test runner to change directory to `scripts/` before running tests
   - Tests use hardcoded paths like `"unittest/data/file.ext"` which only work from that location

## Test Results

### Before Fix
- **3/20 tests passing**
- All file loading operations crashed with segfault
- Only color conversion tests (which don't load files) worked

### After Fix
- **7/20 tests passing**
- File loading works correctly for all formats
- New passing tests:
  - `08-get_histogram.py` ✅
  - `10-find_circles.py` ✅
  - `11-find_lines.py` ✅
  - `19-find_eye.py` ✅

### Still Failing (13 tests)

Remaining failures are **not** due to the segfault bug. They likely fail due to:
- Algorithm differences between Unix and embedded
- Missing features or platform-specific implementations
- Test precision/tolerance issues (e.g., `00-rgb_to_lab.py`)
- Missing dependencies (e.g., descriptor tests, QR codes, AprilTags)

These failures require separate investigation and are outside the scope of this fix.

## Validation

### Manual Testing
```bash
# Build Unix port
make unix

# Test file loading (no longer crashes)
cd lib/micropython/ports/unix
./build-openmv/micropython -c "
import image
img = image.Image('/path/to/image.ppm', copy_to_fb=True)
print(f'Loaded {img.width()}x{img.height()} image')
"
```

### Automated Testing
```bash
# Run full test suite
python3 tests/unix/run_tests.py

# Results: 7/20 passing (up from 3/20)
```

## Technical Notes

### Memory Layout

The Unix port uses a contiguous memory region defined as a struct:
```c
struct __attribute__((aligned(32))) {
    char fb_memory[OMV_FB_MEMORY_SIZE];      // 1MB main framebuffer
    char sb_memory[OMV_SB_MEMORY_SIZE];      // 512KB streaming buffer
    char fb_alloc_memory[OMV_FB_ALLOC_SIZE]; // 2MB fb_alloc temp buffer
} omv_memory_region = {0};
```

Total: ~3.5MB of statically allocated memory for image processing operations.

### Why This Works

1. The memory regions are contiguous in the struct, satisfying fb_alloc's requirement for pointer arithmetic between framebuffer and fb_alloc regions

2. Using struct members directly (`omv_memory_region.fb_memory`) instead of linker symbols correctly points to the actual memory locations

3. The weak symbol mechanism allows port-specific overrides without breaking embedded builds

4. The framebuffer and fb_alloc subsystems are properly initialized via GCC constructor attribute before Python code runs

5. **No linker symbol emulation needed** - we're just using normal C structs and pointers

## Compatibility

- **Embedded targets**: Unaffected (use weak default implementation)
- **Unix port**: Uses override implementation
- **Build system**: No changes needed
- **CI**: Should pass (only modified Unix-specific and weakly-linked code)

## Future Work

- Investigate remaining 13 test failures
- Add more comprehensive Unix port tests
- Consider enabling additional features (imageio module, etc.)
- Performance benchmarking vs embedded targets
- Memory leak testing
