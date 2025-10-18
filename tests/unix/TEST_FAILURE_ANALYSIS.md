# Unix Port Test Failure Analysis

## Summary

7/20 tests passing after fixing the file loading segfault. The remaining 13 failures fall into three categories:

## Test Results by Category

### ✅ Passing Tests (7/20 = 35%)

1. `01-lab_to_rgb.py` - LAB to RGB color conversion
2. `02-rgb_to_grayscale.py` - RGB to grayscale conversion
3. `03-grayscale_to_rgb.py` - Grayscale to RGB conversion
4. `08-get_histogram.py` - Histogram operations
5. `10-find_circles.py` - Hough circle detection
6. `11-find_lines.py` - Line detection (Hough)
7. `19-find_eye.py` - Eye detection

### ❌ Failing Tests (13/20 = 65%)

#### Category 1: Minor Precision Differences (2 tests)

**Test**: `00-rgb_to_lab.py`
- **Expected**: `(75, -40, 34)`
- **Got**: `(75, -41, 32)`
- **Issue**: Floating point rounding differences in LAB color space conversion
- **Impact**: Minimal - values are within ±2 units
- **Fix**: Update test expectations or add tolerance range

**Test**: `09-find_blobs.py`
- **Expected blob[0]**: `[122, 41, 98, 82, 6260, 168, 82]`
- **Got blob[0]**: `[122, 41, 97, 82, 6255, 168, 82]`
- **Issue**: Minor differences in blob detection (width: 98 vs 97, area: 6260 vs 6255)
- **Impact**: Negligible for practical use
- **Fix**: Update test expectations or add tolerance

#### Category 2: Features Disabled in Build (7 tests)

These tests throw `OSError: This function is unavailable on your OpenMV Cam.`

**Test**: `14-find_qrcodes.py`
- **Function**: `find_qrcodes()`
- **Config**: `IMLIB_ENABLE_FIND_QRCODES` defined in config but not active in build

**Test**: `15-find_apriltags.py`
- **Function**: `find_apriltags()`
- **Config**: `IMLIB_ENABLE_FIND_APRILTAGS` defined but not active

**Test**: `16-find_datamatrices.py`
- **Function**: `find_datamatrices()`
- **Config**: `IMLIB_ENABLE_FIND_DATAMATRICES` defined but not active

**Test**: `17-find_barcodes.py`
- **Function**: `find_barcodes()`
- **Config**: `IMLIB_ENABLE_FIND_BARCODES` defined but not active

**Tests**: `04-load_decriptor.py`, `05-save_decriptor.py`, `06-match_descriptor.py`
- **Functions**: `find_keypoints()`, `load_descriptor()`, `match_descriptor()`
- **Config**: `IMLIB_ENABLE_FIND_KEYPOINTS`, `IMLIB_ENABLE_LOAD_DESCRIPTOR` defined but not active
- **Note**: `find_keypoints()` returns `None` instead of throwing error

**Root Cause**: The macros are defined in `boards/UNIX/imlib_config.h` but the build system is not properly including this file during compilation. Investigation shows:

1. `micropython.mk` includes `-I$(OMV_MOD_DIR)/../boards/UNIX` (line 65)
2. MicroPython Unix Makefile includes `-I$(VARIANT_DIR)` (line 49)
3. Test compilation shows macros ARE defined when config is included
4. Object file `py_image.o` references `py_func_unavailable_obj` instead of real functions
5. This indicates `#ifdef IMLIB_ENABLE_XXX` checks fail during compilation

**Attempted Fixes**:
- Added `-I$(OMV_BOARD_CONFIG_DIR)` to `ports/unix/omv_portconfig.mk` (ineffective - env cleared)
- Added `-I$(VARIANT_DIR)` to `boards/UNIX/mpconfigvariant.mk` CFLAGS_EXTRA (ineffective)
- Multiple clean rebuilds (no change)

**Current Status**: Build system issue preventing imlib_config.h from being properly included during USER_C_MODULES compilation.

#### Category 3: Missing Test Data Files (4 tests)

These tests throw `OSError: [Errno 2] ENOENT`

**Test**: `07-haarcascade.py`
- **File needed**: `unittest/data/face.pgm`
- **Available**: `unittest/data/frontalface.cascade` (cascade file exists)
- **Issue**: Test image missing

**Test**: `12-find_line_segments.py`
- **File needed**: `unittest/data/lsd.pgm`
- **Issue**: Test image doesn't exist

**Test**: `13-find_rects.py`
- **File needed**: `unittest/data/rects.pgm`
- **Issue**: Test image doesn't exist

**Test**: `18-find_template.py`
- **File needed**: `unittest/data/template_match.pgm`
- **Available**: `unittest/data/template.pgm` (partial)
- **Issue**: Template match image missing

## Priority Actions

### High Priority: Fix Build System (Category 2)

Need to investigate why `imlib_config.h` macros aren't being seen during compilation:

1. **Verify include path**: Confirm `-I/home/corona/openmv/boards/UNIX` is actually passed to gcc
2. **Check for shadowing**: Search for other `imlib_config.h` files that might be found first
3. **Debug compilation**: Add `-E` flag to see preprocessor output
4. **Alternative approach**: Use `-D` flags to define macros directly in CFLAGS

### Medium Priority: Add Missing Test Data (Category 3)

Options:
1. Create missing test images
2. Mark tests as skipped when data missing
3. Check if files exist in git history or other branches

### Low Priority: Update Test Expectations (Category 1)

Add tolerance ranges for:
- Color space conversions (±2 units acceptable)
- Blob detection (±5 pixels/area acceptable)

## Build System Investigation Notes

**MicroPython Unix Build Flow**:
```
Makefile (top)
  → exports OMV_BOARD_CONFIG_DIR
  → calls make in lib/micropython/ports/unix with env -i (clears env!)
  → passes VARIANT_DIR=/path/to/boards/UNIX
  → Unix Makefile includes $(VARIANT_DIR)/mpconfigvariant.mk
  → mpconfigvariant.mk sets CFLAGS_EXTRA
  → Unix Makefile compiles with: CFLAGS += ... -I$(VARIANT_DIR) $(CFLAGS_EXTRA)
  → USER_C_MODULES uses modules/micropython.mk
  → micropython.mk sets CFLAGS_USERMOD with includes
```

**Key Issue**: Despite all include paths being set, `#ifdef IMLIB_ENABLE_XXX` checks in `py_image.c` evaluate to false during compilation.

**Evidence**:
- `nm py_image.o` shows only `py_func_unavailable_obj` references
- No `py_image_find_qrcodes_obj` or similar symbols
- `nm qrcode.o` is empty (file compiled but no `imlib_find_qrcodes` symbol)
- This means `#ifdef IMLIB_ENABLE_QRCODES` in both files evaluated to false

## Workaround for Development

Current state (7/20 tests passing) is sufficient for:
- Basic image processing algorithm development
- Color conversion operations
- Simple feature detection (circles, lines, eyes)
- Histogram analysis
- File I/O testing

Not available:
- QR codes, barcodes, data matrices, AprilTags
- Feature descriptors (ORB, etc.)
- Template matching
- Advanced shape detection

## Next Steps

1. Add verbose build output to trace actual gcc commands
2. Examine preprocessed source: `gcc -E py_image.c > py_image.i`
3. Check if CMSIS/ARM headers override imlib_config.h defines
4. Consider force-including config: `CFLAGS += -include $(VARIANT_DIR)/imlib_config.h`
5. As last resort: Define macros via CFLAGS: `CFLAGS += -DIMLIB_ENABLE_FIND_QRCODES=1`
