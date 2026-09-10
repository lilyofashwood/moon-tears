#!/usr/bin/env python3
"""
moon_tears.py

A tiny encoder / decoder for the Moon Tears Cipher.

Core idea:
- Payload bytes/chars are converted into base-6 digits.
- Each base-6 digit is stored as a "rain-stack" of combining marks below a carrier letter.
- Decorative carrier letters get 1 mark.
- Payload letters get 2-7 marks:
    digit 0 -> 2 marks
    digit 1 -> 3 marks
    digit 2 -> 4 marks
    digit 3 -> 5 marks
    digit 4 -> 6 marks
    digit 5 -> 7 marks

Default compact mode:
- ascii3: one ASCII character -> three base-6 digits.
- This covers ordinary ASCII text, which is perfect for puzzle payloads like "honeysuckle".

Robust mode:
- utf8_4: one UTF-8 byte -> four base-6 digits.
- This handles arbitrary Unicode text but needs more carrier letters.

Usage:
    python moon_tears.py encode --carrier poem.txt --payload honeysuckle
    python moon_tears.py decode --text encoded.txt
"""

from __future__ import annotations

import argparse
import math
import sys
import unicodedata
from pathlib import Path

MOON_TEAR_MARKS = [
    "\u0325",  # ◌̥  combining ring below
    "\u0323",  # ◌̣  combining dot below
    "\u032C",  # ◌̬  combining caron below
    "\u0330",  # ◌̰  combining tilde below
    "\u032D",  # ◌̭  combining circumflex below
    "\u032E",  # ◌̮  combining breve below
    "\u0331",  # ◌̱  combining macron below
]

BASELINE_HEIGHT = 1
PAYLOAD_HEIGHT_OFFSET = 2


def is_combining_mark(ch: str) -> bool:
    return unicodedata.category(ch).startswith("M")


def is_carrier_char(ch: str) -> bool:
    """Default carrier: alphabetic letters only."""
    return ch.isalpha()


def stack(height: int) -> str:
    if not (0 <= height <= len(MOON_TEAR_MARKS)):
        raise ValueError(f"Unsupported stack height {height}; max is {len(MOON_TEAR_MARKS)}")
    return "".join(MOON_TEAR_MARKS[:height])


def to_base6_fixed(value: int, width: int) -> list[int]:
    if value < 0 or value >= 6 ** width:
        raise ValueError(f"Value {value} does not fit in {width} base-6 digits")
    digits = [0] * width
    for i in range(width - 1, -1, -1):
        digits[i] = value % 6
        value //= 6
    return digits


def from_base6_fixed(digits: list[int]) -> int:
    value = 0
    for digit in digits:
        if digit < 0 or digit > 5:
            raise ValueError(f"Invalid base-6 digit: {digit}")
        value = value * 6 + digit
    return value


def payload_to_digits(payload: str, mode: str = "ascii3") -> list[int]:
    if mode == "ascii3":
        out: list[int] = []
        for ch in payload:
            value = ord(ch)
            if value > 127:
                raise ValueError(
                    f"ascii3 mode only supports ordinary ASCII. Got {ch!r} U+{value:04X}. "
                    "Use mode='utf8_4' for arbitrary Unicode."
                )
            out.extend(to_base6_fixed(value, 3))
        return out

    if mode == "utf8_4":
        out = []
        for byte in payload.encode("utf-8"):
            out.extend(to_base6_fixed(byte, 4))
        return out

    raise ValueError("mode must be 'ascii3' or 'utf8_4'")


def digits_to_payload(digits: list[int], mode: str = "ascii3") -> str:
    width = 3 if mode == "ascii3" else 4 if mode == "utf8_4" else None
    if width is None:
        raise ValueError("mode must be 'ascii3' or 'utf8_4'")
    if len(digits) % width != 0:
        raise ValueError(
            f"Digit count {len(digits)} is not divisible by mode width {width}. "
            "The text may be missing marks or contain extra payload stacks."
        )

    values = [from_base6_fixed(digits[i:i + width]) for i in range(0, len(digits), width)]

    if mode == "ascii3":
        return "".join(chr(v) for v in values)

    return bytes(values).decode("utf-8")


def evenly_spaced_positions(total: int, needed: int) -> set[int]:
    if needed > total:
        raise ValueError(f"Need {needed} carrier letters, but carrier only has {total}")
    if needed == 0:
        return set()
    # Centered even spacing across the eligible carrier field.
    return {
        min(total - 1, max(0, math.floor((i + 0.5) * total / needed)))
        for i in range(needed)
    }


def encode(carrier: str, payload: str, mode: str = "ascii3", spread: bool = True) -> str:
    digits = payload_to_digits(payload, mode=mode)

    carrier_indices = [i for i, ch in enumerate(carrier) if is_carrier_char(ch)]
    if len(digits) > len(carrier_indices):
        raise ValueError(
            f"Payload requires {len(digits)} carrier letters, but carrier has {len(carrier_indices)}. "
            "Use a longer poem/carrier or utf8_4 only when needed."
        )

    if spread:
        chosen_ranks = evenly_spaced_positions(len(carrier_indices), len(digits))
        rank_to_digit = {}
        digit_iter = iter(digits)
        for rank in range(len(carrier_indices)):
            if rank in chosen_ranks:
                rank_to_digit[rank] = next(digit_iter)
    else:
        rank_to_digit = {rank: digit for rank, digit in enumerate(digits)}

    out: list[str] = []
    carrier_rank = 0

    for ch in carrier:
        out.append(ch)
        if is_carrier_char(ch):
            if carrier_rank in rank_to_digit:
                out.append(stack(rank_to_digit[carrier_rank] + PAYLOAD_HEIGHT_OFFSET))
            else:
                out.append(stack(BASELINE_HEIGHT))
            carrier_rank += 1

    return "".join(out)


def decode(text: str, mode: str = "ascii3") -> str:
    digits: list[int] = []

    current_base: str | None = None
    current_marks: list[str] = []

    def flush() -> None:
        nonlocal current_base, current_marks
        if current_base is not None and is_carrier_char(current_base):
            count = sum(1 for mark in current_marks if mark in MOON_TEAR_MARKS)
            if count >= PAYLOAD_HEIGHT_OFFSET:
                digit = count - PAYLOAD_HEIGHT_OFFSET
                if 0 <= digit <= 5:
                    digits.append(digit)
        current_base = None
        current_marks = []

    for ch in text:
        if is_combining_mark(ch):
            current_marks.append(ch)
        else:
            flush()
            current_base = ch
            current_marks = []
    flush()

    return digits_to_payload(digits, mode=mode)


def read_arg_text(value: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if value is None:
        return sys.stdin.read()
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Moon Tears Cipher encoder/decoder")
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode")
    enc.add_argument("--carrier", help="Carrier text, or omit and use stdin")
    enc.add_argument("--carrier-file", help="Path to carrier text file")
    enc.add_argument("--payload", required=True, help="Payload to hide")
    enc.add_argument("--mode", choices=["ascii3", "utf8_4"], default="ascii3")
    enc.add_argument("--no-spread", action="store_true", help="Encode into the first carrier letters instead of spreading")
    enc.add_argument("--out", help="Output file path")

    dec = sub.add_parser("decode")
    dec.add_argument("--text", help="Encoded text, or omit and use stdin")
    dec.add_argument("--text-file", help="Path to encoded text file")
    dec.add_argument("--mode", choices=["ascii3", "utf8_4"], default="ascii3")
    dec.add_argument("--out", help="Output file path")

    args = parser.parse_args()

    if args.command == "encode":
        carrier = read_arg_text(args.carrier, args.carrier_file)
        result = encode(carrier, args.payload, mode=args.mode, spread=not args.no_spread)
    else:
        text = read_arg_text(args.text, args.text_file)
        result = decode(text, mode=args.mode)

    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
