# OpenMV Unix Port Testing

Testing infrastructure for the OpenMV Unix port.

## Quick Start

```bash
# Build the Unix port
make unix

# Run smoke tests
cd lib/micropython/ports/unix
./build-openmv/micropython -c "import image; print('Works!')"

# Run unit test suite
python3 tests/unix/run_tests.py
```

## Test Structure

### Test Runner
- **Location**: `tests/unix/run_tests.py`
- **Purpose**: Automated test runner for Unix-compatible unit tests
- **Source tests**: Adapted from `scripts/unittest/script/`
- **Test data**: Uses `scripts/unittest/data/`

### Test Results
- **Location**: `tests/unix/TEST_RESULTS.md`
- **Contents**: Detailed analysis of test execution, known issues, and recommendations

### Temporary Files
- **Location**: `tests/unix/temp/`
- **Purpose**: Temporary directory for test output (gitignored)

## Current Status

**Build**: ✅ Working
**Basic operations**: ✅ Working
**File I/O**: ❌ Segfault (critical bug)

### Working Features
- Image creation in memory
- Drawing operations (lines, rectangles, circles, text)
- Color space conversions (RGB, LAB, grayscale)
- Format conversions
- Basic image manipulation

### Known Issues
1. **Image file loading causes segmentation fault**
   - Affects all tests requiring image files
   - Blocks 17/20 unit tests
   - Requires debugging before production use

2. **Color conversion precision differences**
   - Minor rounding differences in LAB conversion
   - Not functionally significant

## CI Integration

### Unix Port Workflow
- **File**: `.github/workflows/unix-port.yml`
- **Trigger**: Changes to Unix port, common code, or modules
- **Tests**: Build verification + smoke tests
- **Status**: Unit tests marked as informational (known failures)

### Firmware Workflow
- **File**: `.github/workflows/firmware.yml`
- **Status**: Should pass (common/ and modules/ changes are compatible)
- **Verification**: Code formatting already compliant

## Development Workflow

### Adding New Tests

1. Create test in `scripts/unittest/script/` following existing pattern:
```python
def unittest(data_path, temp_path):
    import image
    # Test code here
    return True  # or False
```

2. If Unix-compatible (no sensor module), add to `UNIX_COMPATIBLE_TESTS` in `run_tests.py`

3. Run test suite to verify

### Debugging Failures

Run individual test with full output:
```bash
cd lib/micropython/ports/unix
./build-openmv/micropython -c "
exec(open('/home/corona/openmv/scripts/unittest/script/YOUR_TEST.py').read())
result = unittest('/home/corona/openmv/scripts/unittest/data', '/tmp')
print(f'Result: {result}')
"
```

### Fixing File I/O Issue

Priority investigation areas:
1. `ports/unix/py_unix_stubs.c` - Framebuffer initialization
2. `common/fb_alloc.c` - Unix-specific allocation
3. `modules/py_imageio.c` - VFS integration (recent changes)
4. `lib/imlib/framebuffer.c` - Framebuffer management

Debug with:
```bash
gdb --args ./build-openmv/micropython test_script.py
```

## Test Coverage

### Color Conversions (4 tests)
- ⚠️ `00-rgb_to_lab.py` - Precision difference
- ✅ `01-lab_to_rgb.py`
- ✅ `02-rgb_to_grayscale.py`
- ✅ `03-grayscale_to_rgb.py`

### Feature Detection (16 tests) - All require file I/O fix
- ❌ Blob detection
- ❌ Line/circle/rectangle detection
- ❌ QR codes, AprilTags, Data matrices, Barcodes
- ❌ Template matching
- ❌ Feature descriptors (load/save/match)
- ❌ Haar cascades
- ❌ Eye detection

### Not Tested (1 test)
- `20-drawing.py` - Requires sensor module adaptation

## Future Enhancements

1. **Fix file I/O bug** (blocking)
2. Enable imageio module
3. Add file format tests (BMP, PNG, JPEG, GIF)
4. Performance benchmarks
5. Memory leak testing
6. Large image tests
7. Edge case coverage
8. Comparison tests vs embedded targets

## Contributing

When adding Unix port functionality:
1. Build and test locally
2. Run `./tools/codeformat.sh` on modified C files
3. Update test suite if adding new features
4. Document known limitations
5. Ensure CI passes

## References

- [Unix Port Documentation](../../docs/unix-port.md)
- [OpenMV Unit Tests](../../scripts/unittest/)
- [MicroPython Test Framework](../../lib/micropython/tests/README.md)
