import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Running dynamic import tests...\n")
import test_dynamic_import
test_dynamic_import.run_all()

print("\nRunning RadioImage tests...\n")
import test_radio_image
test_radio_image.run_all()

print("\n✅ All tests passed.\n")

def encode_bcd_freq_le(freq):
    freq_str = f"{freq:.5f}".replace('.', '').ljust(8, '0')[:8]
    bcd = bytearray()
    for i in range(0, 8, 2):
        lo = int(freq_str[i])
        hi = int(freq_str[i+1])
        bcd.append((hi << 4) | lo)
    return bytes(bcd)

def decode_bcd_freq_le(bcd_bytes):
    digits = ''
    for b in bcd_bytes:
        lo = b & 0x0F
        hi = (b >> 4) & 0x0F
        digits += f"{lo}{hi}"
    return float(digits[:3] + '.' + digits[3:])

class RadioImage:
    def __init__(self, data):
        self.data = bytearray(data)
    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            return cls(f.read())
    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self.data)
    def get_channel_name(self, ch_num):
        offset = 0x1008 + ch_num * 0x10
        raw = self.data[offset:offset+8]
        return raw.rstrip(b'\xFF').decode('ascii', errors='replace')
    def edit_channel(self, ch_num, name, rx_freq, tx_freq):
        if not (0 <= ch_num < 16):
            raise IndexError("Channel number out of range (0-15)")
        if not name.isascii():
            raise ValueError("Channel name must be ASCII")
        base = 0x1008 + ch_num * 0x10
        self.data[base:base+8] = name.encode('ascii')[:8].ljust(8, b'\xFF')
        self.data[base+8:base+12] = encode_bcd_freq_le(rx_freq)
        self.data[base+12:base+16] = encode_bcd_freq_le(tx_freq)
    def list_channels(self):
        print("Channel | Name     | RX Freq   | TX Freq")
        print("--------+----------+-----------+-----------")
        for ch in range(16):
            base = 0x1008 + ch * 0x10
            name = self.get_channel_name(ch)
            rx = self.data[base+8:base+12]
            tx = self.data[base+12:base+16]
            try:
                rx_str = f"{decode_bcd_freq_le(rx):.5f}"
                tx_str = f"{decode_bcd_freq_le(tx):.5f}"
            except Exception:
                rx_str = tx_str = "ERR"
            print(f"{ch:7} | {name:<8} | {rx_str} | {tx_str}")