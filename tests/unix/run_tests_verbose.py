#!/usr/bin/env python3
"""
Verbose Unix port test runner - shows detailed failure information.
"""

import os
import sys
import subprocess

# Path configuration
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
OPENMV_ROOT = os.path.abspath(os.path.join(TEST_DIR, "../.."))
UNITTEST_DATA_DIR = os.path.join(OPENMV_ROOT, "scripts/unittest/data")
UNITTEST_SCRIPT_DIR = os.path.join(OPENMV_ROOT, "scripts/unittest/script")
TEMP_DIR = os.path.join(TEST_DIR, "temp")
MICROPYTHON_BIN = os.path.join(OPENMV_ROOT, "lib/micropython/ports/unix/build-openmv/micropython")

# Tests that work on Unix port
UNIX_COMPATIBLE_TESTS = [
    "00-rgb_to_lab.py",
    "04-load_decriptor.py",
    "05-save_decriptor.py",
    "06-match_descriptor.py",
    "07-haarcascade.py",
    "09-find_blobs.py",
    "12-find_line_segments.py",
    "13-find_rects.py",
    "14-find_qrcodes.py",
    "15-find_apriltags.py",
    "16-find_datamatrices.py",
    "17-find_barcodes.py",
    "18-find_template.py",
]


def run_test(test_path, test_name):
    """Run a single test and return detailed output."""
    os.makedirs(TEMP_DIR, exist_ok=True)

    test_wrapper = f"""
import sys
import os

os.chdir("{os.path.join(OPENMV_ROOT, 'scripts')}")
sys.path.insert(0, "{os.path.dirname(test_path)}")

with open("{test_path}") as f:
    exec(f.read())

data_path = "{UNITTEST_DATA_DIR}"
temp_path = "{TEMP_DIR}"

try:
    result = unittest(data_path, temp_path)
    if result:
        print("TEST_PASSED")
        sys.exit(0)
    else:
        print("TEST_FAILED: unittest() returned False")
        sys.exit(1)
except Exception as e:
    print(f"TEST_EXCEPTION: {{type(e).__name__}}: {{e}}")
    sys.print_exception(e)
    sys.exit(1)
"""

    try:
        result = subprocess.run(
            [MICROPYTHON_BIN, "-c", test_wrapper],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Test timeout after 30s',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }


def main():
    """Run tests with verbose output."""
    if not os.path.exists(MICROPYTHON_BIN):
        print(f"Error: MicroPython binary not found")
        return 1

    print("\n" + "=" * 70)
    print("VERBOSE TEST ANALYSIS - Failing Tests Only")
    print("=" * 70 + "\n")

    for test in sorted(UNIX_COMPATIBLE_TESTS):
        test_path = os.path.join(UNITTEST_SCRIPT_DIR, test)

        if not os.path.exists(test_path):
            print(f"[{test}] NOT FOUND\n")
            continue

        print(f"{'='*70}")
        print(f"TEST: {test}")
        print(f"{'='*70}")

        result = run_test(test_path, test)

        if result['success']:
            print("STATUS: ✅ PASSED\n")
        else:
            print("STATUS: ❌ FAILED")
            print(f"\nSTDOUT:\n{result['stdout']}")
            if result['stderr']:
                print(f"\nSTDERR:\n{result['stderr']}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
