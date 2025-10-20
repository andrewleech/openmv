#!/usr/bin/env python3
"""
Unix port test runner for OpenMV image processing library.

Runs adapted unit tests from scripts/unittest that work without hardware.
"""

import os
import sys
import subprocess
import gc

# Path configuration
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
OPENMV_ROOT = os.path.abspath(os.path.join(TEST_DIR, "../.."))
UNITTEST_DATA_DIR = os.path.join(OPENMV_ROOT, "scripts/unittest/data")
UNITTEST_SCRIPT_DIR = os.path.join(OPENMV_ROOT, "scripts/unittest/script")
TEMP_DIR = os.path.join(TEST_DIR, "temp")
MICROPYTHON_BIN = os.path.join(OPENMV_ROOT, "lib/micropython/ports/unix/build-openmv/micropython")

# Tests that work on Unix port (no sensor module required)
UNIX_COMPATIBLE_TESTS = [
    "00-rgb_to_lab.py",
    "01-lab_to_rgb.py",
    "02-rgb_to_grayscale.py",
    "03-grayscale_to_rgb.py",
    "04-load_decriptor.py",
    "05-save_decriptor.py",
    "06-match_descriptor.py",
    "07-haarcascade.py",
    "08-get_histogram.py",
    "09-find_blobs.py",
    "10-find_circles.py",
    "11-find_lines.py",
    "12-find_line_segments.py",
    "13-find_rects.py",
    "14-find_qrcodes.py",
    "15-find_apriltags.py",
    "16-find_datamatrices.py",
    "17-find_barcodes.py",
    "18-find_template.py",
    "19-find_eye.py",
    # 20-drawing.py requires sensor module (hardware-only)
]


def print_result(test, result):
    """Print test result with consistent formatting."""
    s = f"Test ({test})"
    padding = "." * (60 - len(s))
    print(s + padding + result)


def run_test(test_path, test_name):
    """
    Run a single test script.

    Returns True if test passes, False otherwise.
    """
    # Create temporary directory if it doesn't exist
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Build test wrapper that calls the unittest function
    # NOTE: Tests use hardcoded paths like "unittest/data/file.ext"
    # so we need to run from the scripts directory
    test_wrapper = f"""
import sys
import os

# Change to scripts directory where unittest/ exists
os.chdir("{os.path.join(OPENMV_ROOT, 'scripts')}")

sys.path.insert(0, "{os.path.dirname(test_path)}")

# Load the test module
with open("{test_path}") as f:
    exec(f.read())

# Run the unittest function
data_path = "{UNITTEST_DATA_DIR}"
temp_path = "{TEMP_DIR}"

try:
    result = unittest(data_path, temp_path)
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""

    try:
        result = subprocess.run(
            [MICROPYTHON_BIN, "-c", test_wrapper],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return True, "PASSED"
        else:
            return False, "FAILED"

    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except FileNotFoundError:
        return False, "BINARY_NOT_FOUND"
    except Exception as e:
        return False, f"ERROR: {str(e)}"


def main():
    """Run all Unix-compatible tests."""
    if not os.path.exists(MICROPYTHON_BIN):
        print(f"Error: MicroPython binary not found at {MICROPYTHON_BIN}")
        print("Run 'make unix' first to build the Unix port.")
        return 1

    if not os.path.exists(UNITTEST_DATA_DIR):
        print(f"Error: Test data directory not found at {UNITTEST_DATA_DIR}")
        return 1

    print()
    print("=" * 70)
    print("OpenMV Unix Port Test Suite")
    print("=" * 70)
    print()

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test in sorted(UNIX_COMPATIBLE_TESTS):
        test_path = os.path.join(UNITTEST_SCRIPT_DIR, test)

        if not os.path.exists(test_path):
            print_result(test, "NOT_FOUND")
            continue

        total_tests += 1
        success, result = run_test(test_path, test)

        print_result(test, result)

        if success:
            passed_tests += 1
        else:
            failed_tests += 1

    print()
    print("=" * 70)
    print(f"Results: {passed_tests}/{total_tests} passed, {failed_tests} failed")
    print("=" * 70)
    print()

    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
