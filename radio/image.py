def encode_bcd_freq_le(freq):
    """Encode float frequency like 446.00625 into 4-byte little-endian BCD."""
    freq_str = f"{freq:.5f}".replace('.', '').ljust(8, '0')[:8]
    bcd = bytearray()
    for i in range(0, 8, 2):
        lo = int(freq_str[i])
        hi = int(freq_str[i+1])
        bcd.append((hi << 4) | lo)
    return bytes(bcd)


def decode_bcd_freq_le(bcd_bytes):
    """Decode 4-byte little-endian BCD to float (e.g. 0x62 0x60 0x44 0x00 -> 446.00625)."""
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
        if not (0 <= ch_num < 16):
            raise IndexError("Channel number out of range (0-15)")
        offset = 0x1008 + ch_num * 0x10
        raw = self.data[offset:offset+8]
        return raw.rstrip(b'\xFF').decode('ascii', errors='replace')

    def edit_channel_name(self, ch_num, name):
        if not (0 <= ch_num < 16):
            raise IndexError("Channel number out of range (0-15)")
        offset = 0x1008 + ch_num * 0x10
        name_bytes = name.encode('ascii')[:8].ljust(8, b'\xFF')
        self.data[offset:offset+8] = name_bytes

    def clear_channel(self, ch_num):
        if not (0 <= ch_num < 128):
            raise IndexError("Channel number out of range (0-127)")
        base = 0x0020 + ch_num * 0x20
        self.data[base:base + 0x20] = b'\xFF' * 0x20

    def edit_channel(self, ch_num, name, rx_freq, tx_freq):
        """Edit channel name and RX/TX frequencies."""
        if not (0 <= ch_num < 16):
            raise IndexError("Channel number out of range (0-15)")

        # Edit name
        name_offset = 0x1008 + ch_num * 0x10
        name_bytes = name.encode('ascii')[:8].ljust(8, b'\xFF')
        self.data[name_offset:name_offset+8] = name_bytes

        # Edit RX/TX frequency
        chan_base = 0x0020 + ch_num * 0x20
        self.data[chan_base + 0x04 : chan_base + 0x08] = encode_bcd_freq_le(rx_freq)
        self.data[chan_base + 0x08 : chan_base + 0x0C] = encode_bcd_freq_le(tx_freq)

    def list_channels(self):
        print("Channel | Name     | RX Freq   | TX Freq   | Raw")
        print("--------+----------+-----------+-----------+--------------------------------")

        for ch in range(16):
            try:
                name = self.get_channel_name(ch)
                chan_base = 0x0020 + ch * 0x20
                rx = self.data[chan_base + 0x04 : chan_base + 0x08]
                tx = self.data[chan_base + 0x08 : chan_base + 0x0C]

                rx_str = f"{decode_bcd_freq_le(rx):.5f}"
                tx_str = f"{decode_bcd_freq_le(tx):.5f}"
                raw_str = ' '.join(f"{b:02X}" for b in self.data[chan_base:chan_base+0x20])

                print(f"{ch:7} | {name:<8} | {rx_str} | {tx_str} | {raw_str}")
            except Exception:
                print(f"{ch:7} | ERROR reading channel")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 radio_image.py <radio.img>")
        sys.exit(1)
    img = RadioImage.load(sys.argv[1])
    img.list_channels()
