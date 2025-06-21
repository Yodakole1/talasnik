import sys
import importlib

def test_dynamic_import():
    try:
        mod = importlib.import_module("radio.uv5r")
        assert hasattr(mod, "dump_radio")
        print("✅ PASS: Dynamic import for uv5r")
    except ImportError:
        print("❌ FAIL: Dynamic import for uv5r")
        sys.exit(1)

    try:
        importlib.import_module("radio.nonexistent")
        print("❌ FAIL: Import should fail for nonexistent model")
        sys.exit(1)
    except ImportError:
        print("✅ PASS: Import fails for nonexistent model")

def run_all():
    test_dynamic_import()

if __name__ == "__main__":
    run_all()