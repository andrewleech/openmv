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
- ✅ Firmware rebuilt successfully using Docker build system
- ✅ Firmware flashed via probe-rs with CherryDAP debug probe
- ✅ Cascade loads successfully from /sdcard
- ✅ Image loads successfully (300x200) from /sdcard
- ❌ **Detection returns 0 objects (identical to Unix port behavior)**
- ℹ️  Initial path confusion: `/sd` returns ENODEV, correct path is `/sdcard`

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

### Detection Issue (0 objects on Both Platforms)
**Critical Finding:** Both Unix port and OPENMV4 hardware return 0 detections with identical test conditions.

This rules out platform-specific issues:
- ❌ Not a 64-bit vs 32-bit pointer issue
- ❌ Not a floating point precision difference
- ❌ Not a Unix-specific memory layout issue
- ✅ Likely a fundamental bug in haarcascade detection algorithm

The bug affects both architectures (x86_64 and ARM Cortex-M7), suggesting:
1. Logic error in cascade evaluation algorithm
2. Incorrect threshold or scaling parameter handling
3. Bug in integral image computation that affects all platforms
4. Issue with how rectangles extending beyond window bounds are handled

Further investigation needed:
- Add debug logging to track cascade stage evaluations
- Verify integral image values match expected computation
- Test with different threshold/scale parameters
- Compare with OpenCV's Viola-Jones implementation
- Verify rectangle coordinate calculations when features extend beyond window

## Test Results

**Overall Unix Port:** 9/20 tests passing (45%)

**Haarcascade specific:**
- Unix port: FAILED (no crash, 0 detections, expected 2 faces)
- OPENMV4 hardware: FAILED (no crash, 0 detections, expected 2 faces)
- **Both platforms exhibit identical failure mode**

## Commits

1. `fbd6f70b` - Initial crash fixes (dangling pointers, pointer cast)
2. `f0ea5e8f` - Document buffer overflow issue
3. `480e0b1a` - Fix buffer overflow with correct row allocation

## Build Environment Resolution

**Docker Build System Works:**
- Direct `make` builds fail with ARM/Thumb relocation errors (toolchain issue)
- Docker-based build system (`docker/Makefile`) builds successfully
- Firmware binary generated: `docker/build/OPENMV4/bin/openmv.bin` (1.9MB)
- Build includes ImageIO support as configured in `boards/OPENMV4/imlib_config.h`

**Firmware Flashing (RESOLVED):**
- `dfu-util` fails with "Device is unable to write memory" error
- `pydfu.py` has Python 3.12 compatibility issues (`inspect.getargspec` deprecated)
- ✅ **Solution:** Used probe-rs with CherryDAP debug probe
  - `probe-rs download --chip STM32H743VITx --probe 0d28:0204 firmware.elf`
  - Flashing completed in ~65 seconds
  - Device boots successfully with ImageIO support enabled

## Recommendations

1. **For haarcascade detection issue (affects both Unix and hardware):**
   - Add detailed debug logging to track:
     - Integral image computation values
     - Stage-by-stage cascade evaluation
     - Rectangle feature calculations
     - Threshold comparisons at each stage
   - Test with alternative cascade files (eye.cascade, smile.cascade)
   - Compare implementation against OpenCV's Viola-Jones reference
   - Verify scaling and windowing logic when features extend beyond window bounds
   - Check if issue exists in older firmware versions (regression test)

2. **Hardware testing infrastructure (COMPLETED):**
   - ✅ Firmware builds successfully using Docker build system
   - ✅ probe-rs flashing works with CherryDAP debug probe
   - ✅ Identical test runs successfully on both Unix and OPENMV4
   - ℹ️  Note: SD card mount point is `/sdcard` not `/sd`

3. **General:**
   - Consider validating cascade files don't have rectangles extending too far beyond window
   - Document integral image buffer requirements in code
   - Add runtime validation for cascade file format
   - Document probe-rs flashing procedure for OPENMV4
