#!/usr/bin/env python3
import importlib
import platform
import sys


def _check_package(name: str) -> None:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "unknown")
        print(f"[OK] {name}: {version}")
    except Exception as exc:
        print(f"[MISSING] {name}: {exc}")


def main() -> int:
    print("=== System ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")

    print("\n=== Packages ===")
    for pkg in ["torch", "transformers", "pandas", "numpy", "sklearn", "yaml"]:
        _check_package(pkg)
    print("\n=== Compute ===")
    try:
        import torch

        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU count: {torch.cuda.device_count()}")
            for idx in range(torch.cuda.device_count()):
                print(f"- GPU {idx}: {torch.cuda.get_device_name(idx)}")
        else:
            mps_ok = getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
            print(f"MPS available (Apple): {bool(mps_ok)}")
            if not mps_ok:
                print("No accelerator detected. Colab GPU is recommended.")
    except Exception as exc:
        print(f"Could not check torch compute backend: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
