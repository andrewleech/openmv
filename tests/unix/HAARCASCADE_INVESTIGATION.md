# Haarcascade Investigation Summary

## Bugs Fixed in Unix Port

### 1. Pointer-to-int Cast (64-bit compatibility)
**File:** `lib/imlib/haar.c:211`
**Issue:** `(uint32_t) buf % 4` truncates 64-bit pointers
**Fix:** Changed to `(uintptr_t) buf % 4`

### 2. Dangling Pointer Bug
**File:** `lib/imlib/haar.c:195-250`
**Issue:** In `mp_get_buffer()` path, cascade arrays pointed directly into file buffer which gets freed when file closes, causing use-after-free
**Fix:** Allocate separate memory with `m_malloc()` and `memcpy()` data instead of using `cascade_buffer_read()` helper

### 3. Buffer Overflow in Integral Image
**File:** `lib/imlib/haar.c:120-127`
**Issue:** Cascade rectangles extend beyond window (frontalface.cascade has max y+h=40 for 24x24 window), but integral image only allocated window.h+1=25 rows
**Fix:** Allocate `window.h * 2 + 1` rows to accommodate extended rectangles

## Current Status

### Unix Port
- ✅ No crashes - cascade loads successfully
- ✅ Image loads successfully
- ❌ Detection returns 0 objects (expected 2 faces)

### Hardware Test (OPENMV4)
- ✅ Cascade uploads and loads successfully
- ❌ Cannot test detection - firmware lacks ImageIO support
- ℹ️  Hardware firmware would need IMLIB_ENABLE_IMAGE_IO=1 to test with PGM files

## Technical Details

### Cascade File Analysis (frontalface.cascade)
```
Window: 24x24
Stages: 15
Features: 1109
Rectangles: 2390
Max rectangle extent: y+h=40, x+w=44 (extends beyond 24x24 window)
```

### Integral Image Scaling
The scaling ratio in `imlib_integral_mw_scale()` correctly maps integral image row indices to source image regardless of allocated height:
```c
sum->y_ratio = (roi->h << 16) / h  // h is scaled height, not integral height
```
Therefore allocating more rows is valid as long as they stay within source image bounds.

### Detection Issue (0 objects on Unix)
Unknown root cause. Possibilities:
1. Platform-specific floating point differences
2. Memory layout affecting algorithm behavior
3. Bug in detection algorithm that manifests on 64-bit
4. Cascade file compatibility issue

Further investigation needed with:
- Detailed logging of intermediate values
- Comparison with known-working hardware results
- Testing with different cascade files
- Verification of integral image computation

## Test Results

**Overall Unix Port:** 9/20 tests passing (45%)

**Haarcascade specific:**
- Unix: FAILED (no crash, but 0 detections)
- Hardware: Cannot test (ImageIO not compiled)

## Commits

1. `fbd6f70b` - Initial crash fixes (dangling pointers, pointer cast)
2. `f0ea5e8f` - Document buffer overflow issue
3. `480e0b1a` - Fix buffer overflow with correct row allocation

## Recommendations

1. **For Unix port haarcascade detection issue:**
   - Add debug logging to compare Unix vs embedded integral image values
   - Test with simpler cascade files
   - Verify fb_alloc behavior on Unix matches embedded

2. **For hardware testing:**
   - Rebuild OPENMV4 firmware with `IMLIB_ENABLE_IMAGE_IO=1`
   - Run identical test on hardware to establish baseline

3. **General:**
   - Consider validating cascade files don't have rectangles extending too far beyond window
   - Document integral image buffer requirements in code
