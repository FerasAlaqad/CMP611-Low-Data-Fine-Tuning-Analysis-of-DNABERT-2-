#!/usr/bin/env python3
import argparse
import pathlib
import zipfile

import gdown


GUE_FILE_ID = "1uOrwlf07qGQuruXqGXWMpPn8avBoW7T-"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and extract GUE dataset.")
    parser.add_argument("--out-dir", type=str, default="data/raw", help="Output directory.")
    parser.add_argument(
        "--filename",
        type=str,
        default="GUE.zip",
        help="Downloaded archive filename inside out-dir.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_path = out_dir / args.filename
    if not zip_path.exists():
        print(f"Downloading GUE to: {zip_path}")
        gdown.download(id=GUE_FILE_ID, output=str(zip_path), quiet=False)
    else:
        print(f"Archive already exists: {zip_path}")

    print("Extracting archive...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)

    print(f"Done. Check extracted folders under: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
