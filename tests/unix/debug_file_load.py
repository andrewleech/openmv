#!/usr/bin/env python3
"""
Minimal test case for debugging file loading segfault.
Run with: cd lib/micropython/ports/unix && ./build-openmv/micropython ../../../../tests/unix/debug_file_load.py
"""

import image
import sys
import gc

# Test paths - using absolute paths
TEST_IMAGE_PPM = "/home/corona/openmv/scripts/unittest/data/blobs.ppm"
TEST_IMAGE_PGM = "/home/corona/openmv/scripts/unittest/data/dennis.pgm"

print("=" * 70)
print("Image File Loading Debug Test")
print("=" * 70)

# Test 1: Verify in-memory operations work
print("\n[Test 1] In-memory image creation...")
try:
    img = image.Image(100, 100, image.RGB565)
    print(f"  ✅ Created {img.width()}x{img.height()} image")
    del img
    gc.collect()
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Load image WITHOUT copy_to_fb
print("\n[Test 2] Load image WITHOUT copy_to_fb...")
try:
    print(f"  Loading: {TEST_IMAGE_PGM}")
    img = image.Image(TEST_IMAGE_PGM, copy_to_fb=False)
    print(f"  ✅ Loaded {img.width()}x{img.height()} image")
    del img
    gc.collect()
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Load image WITH copy_to_fb (EXPECTED TO CRASH)
print("\n[Test 3] Load image WITH copy_to_fb (may crash)...")
try:
    print(f"  Loading: {TEST_IMAGE_PGM}")
    print("  About to call image.Image() with copy_to_fb=True...")
    img = image.Image(TEST_IMAGE_PGM, copy_to_fb=True)
    print(f"  ✅ Loaded {img.width()}x{img.height()} image")
    del img
    gc.collect()
except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test completed without crash")
print("=" * 70)
