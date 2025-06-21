import argparse
from radio.image import RadioImage
from radio.uv5r import dump_radio, upload_radio

def main():
    parser = argparse.ArgumentParser(description="Baofeng UV-5R CLI Tool")
    parser.add_argument('-m', '--mode', choices=['dump', 'upload', 'edit', 'list', 'batch-edit', 'clear'], required=True)
    parser.add_argument('-p', '--port', help="Serial port for radio (required for dump/upload)")
    parser.add_argument('-f', '--file', required=True, help="Radio image file")
    parser.add_argument('--edit-channel', type=int, help="Channel number to edit or clear")
    parser.add_argument('--name', help="Channel name (ASCII, max 7 chars)")
    parser.add_argument('--freq', type=float, help="RX frequency (MHz)")
    parser.add_argument('--txfreq', type=float, help="TX frequency (MHz)")
    parser.add_argument('--batch-start', type=int, help="Batch edit: start channel")
    parser.add_argument('--batch-end', type=int, help="Batch edit: end channel")
    args = parser.parse_args()

    if args.mode == 'dump':
        if not args.port:
            print("Port required for dump.")
            return
        dump_radio(args.port, args.file)

    elif args.mode == 'upload':
        if not args.port:
            print("Port required for upload.")
            return
        upload_radio(args.port, args.file)

    elif args.mode == 'edit':
        if args.edit_channel is None or args.name is None or args.freq is None or args.txfreq is None:
            print("edit mode requires --edit-channel, --name, --freq, --txfreq")
            return
        img = RadioImage.load(args.file)
        img.edit_channel(args.edit_channel, args.name, args.freq, args.txfreq)
        img.save(args.file)
        print(f"✅ Channel {args.edit_channel} updated.")

    elif args.mode == 'clear':
        if args.edit_channel is None:
            print("clear mode requires --edit-channel")
            return
        img = RadioImage.load(args.file)
        img.clear_channel(args.edit_channel)
        img.save(args.file)
        print(f"✅ Channel {args.edit_channel} cleared.")

    elif args.mode == 'list':
        img = RadioImage.load(args.file)
        img.list_channels()

    elif args.mode == 'batch-edit':
        if args.batch_start is None or args.batch_end is None or args.freq is None or args.txfreq is None:
            print("batch-edit mode requires --batch-start, --batch-end, --freq, --txfreq")
            return
        img = RadioImage.load(args.file)
        for ch in range(args.batch_start, args.batch_end + 1):
            name = f"CH{ch}"
            img.edit_channel(ch, name, args.freq, args.txfreq)
            print(f"Edited channel {ch}: {name} {args.freq} {args.txfreq}")
        img.save(args.file)
        print(f"✅ Batch edit complete for channels {args.batch_start}-{args.batch_end}.")

if __name__ == "__main__":
    main()