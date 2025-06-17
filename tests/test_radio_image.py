import sys
import os
from radio.image import RadioImage

def assert_equal(a, b, msg):
    if a != b:
        print(f"❌ FAIL: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

def test_edit_channel_out_of_bounds():
    dummy = bytearray(4096)
    img = RadioImage(dummy)
    try:
        img.edit_channel(200, "TEST", 446.0, 446.0)
        print("❌ FAIL: Out-of-bounds channel edit did not raise error")
        sys.exit(1)
    except Exception:
        print("✅ PASS: Out-of-bounds channel edit raises error")

def test_channel_name_encoding():
    dummy = bytearray(4096)
    img = RadioImage(dummy)
    try:
        img.edit_channel(0, "ČĆŽŠĐ", 446.0, 446.0)
        print("❌ FAIL: Non-ASCII channel name did not raise error")
        sys.exit(1)
    except ValueError:
        print("✅ PASS: Non-ASCII channel name raises ValueError")

def test_image_save_load():
    dummy = bytearray(range(256)) * 10
    path = "tests/test_image.img"
    img = RadioImage(dummy)
    img.save(path)
    try:
        reloaded = RadioImage.load(path)
        assert_equal(reloaded.data, dummy, "Image load/save matches original")
    finally:
        if os.path.exists(path):
            os.remove(path)

def test_edit_channel():
    dummy = bytearray(4096)
    img = RadioImage(dummy)
    img.edit_channel(1, "HELLO", 446.0, 446.0)
    expected = b"HELLO"
    actual = img.data[0x30:0x30+len(expected)]
    assert_equal(actual, expected, "Channel 1 name set correctly")

def test_load_image_from_radio_sim():
    dummy = bytearray(range(256)) * 10
    path = "tests/test_radio_dump.img"
    with open(path, "wb") as f:
        f.write(dummy)
    try:
        from radio.uv5r import load_image
        img = load_image(path)
        assert isinstance(img, RadioImage), "Loaded object is a RadioImage"
        assert_equal(img.data, dummy, "Radio driver load_image matches dumped data")
    finally:
        if os.path.exists(path):
            os.remove(path)

def run_all():
    test_edit_channel_out_of_bounds()
    test_channel_name_encoding()
    test_image_save_load()
    test_edit_channel()
    test_load_image_from_radio_sim()

if __name__ == "__main__":
    run_all()