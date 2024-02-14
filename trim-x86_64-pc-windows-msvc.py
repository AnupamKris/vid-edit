import os
import argparse

def main(input_path, start, end, output):
    print("Starting...", flush=True)
    os.system(f"ffmpeg-x86_64-pc-windows-msvc.exe -i {input_path} -ss {start} -t {end} -c copy {output} -y")
    print("Done!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video cutting tool")
    parser.add_argument("inp", type=str, help="Path to the video file")
    parser.add_argument("start", type=float, help="Start time")
    parser.add_argument("end", type=float, help="End time")
    parser.add_argument("out", type=str, help="Output file path")
    args = parser.parse_args()

    main(args.inp, args.start, args.end, args.out)