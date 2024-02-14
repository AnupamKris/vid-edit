import os
import argparse

def main(output, vidfile):
    
    print("Files!", vidfile, flush=True)
    print(f'ffmpeg-x86_64-pc-windows-msvc.exe -f concat -safe 0 -i {vidfile} -c copy {output}')
    os.system(f'ffmpeg-x86_64-pc-windows-msvc.exe -f concat -safe 0 -i {vidfile} -c copy {output} -y')
    # os.system(f'ffmpeg -loglevel quiet -i "concat:{videofiles}" -c copy {output} -y')
    print("Done!", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video concatenation tool")
    parser.add_argument("out", type=str, help="Output file path")
    parser.add_argument("inp", type=str, nargs='+', help="Input video files")
    args = parser.parse_args()

    main(args.out, *args.inp)