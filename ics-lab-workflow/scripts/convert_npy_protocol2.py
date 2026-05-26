#!/usr/bin/env python3
"""convert_npy_protocol2.py — Re-save a NumPy .npy dict with pickle protocol 2.

Motivation: NumPy 1.24+ on Python 3.8+ saves allow_pickle dicts with pickle
protocol 5 by default. Platforms running Python 3.7 + NumPy 1.19 (common in
Chinese university ICS/MLU course environments) can't read protocol 5.

This script reads the weight file, re-pickles it with protocol 2, and writes
a compatible .npy file that loads on NumPy 1.19+ / Python 3.6+.

Usage:
    python convert_npy_protocol2.py <input.npy> [output.npy]
    # Default output: overwrites input

Dependencies: numpy (any version)
"""

import sys, os, struct, pickle, io
import numpy as np


def convert_npy(input_path, output_path=None):
    if output_path is None:
        output_path = input_path

    # Load the dict (works on source machine with numpy available)
    p = np.load(input_path, allow_pickle=True).item()
    print(f"Loaded: { {k: f'{v.shape} {v.dtype}' for k, v in p.items()} }")

    # Re-pickle with protocol 2 (compatible Python 2.7+)
    buf = io.BytesIO()
    pickle.dump(p, buf, protocol=2)
    data = buf.getvalue()

    # Build .npy format manually
    header = "{'descr': '|O', 'fortran_order': False, 'shape': (), }"
    header_bytes = header.encode('ascii')
    pad = (16 - (10 + len(header_bytes)) % 16) % 16
    header_bytes += b' ' * pad + b'\n'

    with open(output_path, 'wb') as f:
        f.write(b'\x93NUMPY')                    # magic
        f.write(b'\x01\x00')                     # version 1.0
        f.write(struct.pack('<H', len(header_bytes)))  # header length (uint16 LE)
        f.write(header_bytes)                    # header
        f.write(data)                            # pickled data (protocol 2)

    # Verify
    p2 = np.load(output_path, allow_pickle=True).item()
    for k in p:
        assert np.array_equal(p[k], p2[k]), f"Mismatch on key '{k}'!"
    print(f"Verified OK. Saved: {output_path} ({len(data)} bytes pickle data)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert_npy(inp, out)
