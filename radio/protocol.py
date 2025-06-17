import serial
import time

class UV5RProtocol:
    def __init__(self, port):
        self.ser = serial.Serial(port, 9600, timeout=1)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def _handshake(self, handshakes, sleep_between=0.03, debug_label=""):
        self.ser.setDTR(True)
        self.ser.setRTS(True)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        time.sleep(0.5)
        for magic in handshakes:
            print(f"{debug_label}Trying magic: {magic.hex()}")
            # Try block write
            self.ser.write(magic)
            time.sleep(0.3)
            ack = self.ser.read(1)
            print(f"{debug_label}ACK (block): {ack!r}")
            if ack == b'\x06':
                self.ser.write(b'\x02')
                ident = bytearray()
                for _ in range(12):
                    b = self.ser.read(1)
                    ident += b
                    if b == b'\xdd':
                        break
                print(f"{debug_label}Ident: {ident.hex()}")
                self.ser.write(b'\x06')
                final_ack = self.ser.read(1)
                print(f"{debug_label}Final ACK: {final_ack!r}")
                if final_ack != b'\x06':
                    raise Exception(f"Radio refused clone {debug_label}")
                return ident
            # Try byte-by-byte
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            for b in magic:
                self.ser.write(bytes([b]))
                time.sleep(sleep_between)
            time.sleep(0.3)
            ack = self.ser.read(1)
            print(f"{debug_label}ACK (byte): {ack!r}")
            if ack == b'\x06':
                self.ser.write(b'\x02')
                ident = bytearray()
                for _ in range(12):
                    b = self.ser.read(1)
                    ident += b
                    if b == b'\xdd':
                        break
                print(f"{debug_label}Ident: {ident.hex()}")
                self.ser.write(b'\x06')
                final_ack = self.ser.read(1)
                print(f"{debug_label}Final ACK: {final_ack!r}")
                if final_ack != b'\x06':
                    raise Exception(f"Radio refused clone {debug_label}")
                return ident
        raise Exception(f"No ACK from radio {debug_label}")

    def init_radio(self):
        # UV-5R handshake
        return self._handshake([b'\x50\xbb\xff\x20\x12\x07\x25'], debug_label="(UV-5R) ")

    def init_radio_upload(self):
        # Try both handshake bytes for upload
        return self._handshake(
            [b'\x50\xbb\xff\x20\x12\x07\x27', b'\x50\xbb\xff\x20\x12\x07\x25'],
            debug_label="(UV-5R upload) "
        )

    def read_block(self, address, size, first=False):
        self.ser.write(bytes([0x53, (address >> 8) & 0xFF, address & 0xFF, size]))
        if not first and self.ser.read(1) != b'\x06':
            raise Exception("Read block NACK")
        header = self.ser.read(4)
        if header[0] != 0x58:
            raise Exception("Invalid block header")
        return self.ser.read(size)

    def send_block(self, address, data):
        head = [0x58, (address >> 8) & 0xFF, address & 0xFF, len(data)]
        self.ser.write(bytes(head) + data)
        ack = self.ser.read(1)
        return ack == b'\x06'
