from .protocol import UV5RProtocol
from .image import RadioImage

IDENT_SIZE = 8
BLOCK_SIZE = 0x40
MAIN_BLOCKS = 0x60
EXTRA_BLOCK_START = 0x7B
EXTRA_BLOCK_END = 0x80
UPLOAD_BLOCK_SIZE = 0x10
UPLOAD_MAIN_SIZE = 0x1800
UPLOAD_EXTRA_SIZE = 0x140

def dump_radio(port, out_file):
    """Dump the radio memory to a file."""
    proto = UV5RProtocol(port)
    ident = proto.init_radio()
    data = bytearray(ident)
    try:
        for i in range(MAIN_BLOCKS):
            block = proto.read_block(i * BLOCK_SIZE, BLOCK_SIZE, first=(i == 0))
            data += block
            print(f"Dumped block {i+1}/{MAIN_BLOCKS}")
        for i in range(EXTRA_BLOCK_START, EXTRA_BLOCK_END):
            block = proto.read_block(i * BLOCK_SIZE, BLOCK_SIZE)
            data += block
            print(f"Dumped extra block {i-EXTRA_BLOCK_START+1}/{EXTRA_BLOCK_END-EXTRA_BLOCK_START}")
        with open(out_file, 'wb') as f:
            f.write(data)
        print(f"✅ Dump complete: {out_file}")
    except Exception as e:
        print(f"❌ Dump failed: {e}")
        raise

def upload_radio(port, in_file):
    """Upload a memory image file to the radio."""
    proto = UV5RProtocol(port)
    ident = proto.init_radio_upload()  # Use the upload handshake!
    print(f"Radio ident: {ident.hex()}")
    try:
        with open(in_file, 'rb') as f:
            data = f.read()
        if data[:IDENT_SIZE] != ident[:IDENT_SIZE]:
            raise Exception("Ident mismatch")
        if len(data) < (IDENT_SIZE + UPLOAD_MAIN_SIZE + UPLOAD_EXTRA_SIZE):
            raise Exception("Image file too small")
        # Main memory blocks (0x10 bytes each)
        main_blocks = [data[IDENT_SIZE:IDENT_SIZE+UPLOAD_MAIN_SIZE][j:j+UPLOAD_BLOCK_SIZE] 
                       for j in range(0, UPLOAD_MAIN_SIZE, UPLOAD_BLOCK_SIZE)]
        for i, block in enumerate(main_blocks):
            ok = proto.send_block(i * UPLOAD_BLOCK_SIZE, block)
            print(f"Uploaded block {i+1}/{len(main_blocks)}: {'OK' if ok else 'FAIL'}")
            if not ok:
                raise Exception(f"Radio NACK at main block {i}")
        # Extra memory blocks
        extra_offset = IDENT_SIZE + UPLOAD_MAIN_SIZE
        extra_blocks = [data[extra_offset:extra_offset+UPLOAD_EXTRA_SIZE][j:j+UPLOAD_BLOCK_SIZE] 
                        for j in range(0, UPLOAD_EXTRA_SIZE, UPLOAD_BLOCK_SIZE)]
        for i, block in enumerate(extra_blocks):
            ok = proto.send_block(0x1EC0 + i * UPLOAD_BLOCK_SIZE, block)
            print(f"Uploaded extra block {i+1}/{len(extra_blocks)}: {'OK' if ok else 'FAIL'}")
            if not ok:
                raise Exception(f"Radio NACK at extra block {i}")
        print(f"✅ Upload complete: {in_file}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise

def load_image(path):
    """Load a radio image from file."""
    return RadioImage.load(path)

def save_image(img, path):
    """Save a radio image to file."""
    img.save(path)