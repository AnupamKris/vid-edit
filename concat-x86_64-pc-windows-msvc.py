import os
import argparse

def main(output, *videos):
    print("Starting...", flush=True)
    videofiles = "|".join([f"{i}" for i in videos])
    print("Files!", videofiles, flush=True)
    os.system(f'ffmpeg-x86_64-pc-windows-msvc.exe -loglevel quiet -i "concat:{videofiles}" -c copy {output}')
    # os.system(f'ffmpeg -loglevel quiet -i "concat:{videofiles}" -c copy {output} -y')
    print("Done!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video concatenation tool")
    parser.add_argument("out", type=str, help="Output file path")
    parser.add_argument("inp", type=str, nargs='+', help="Input video files")
    args = parser.parse_args()

    main(args.out, *args.inp)