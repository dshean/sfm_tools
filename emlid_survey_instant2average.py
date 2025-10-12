#! /usr/bin/env python
# David Shean
# 10/3/25

# Script to modify an emlid Survey csv to create 1-second averaging for points, instead of Instant

# Modified from ChatGPT output 

import pandas as pd
from datetime import timedelta
import os

def adjust_emlid_csv(input_csv, output_csv=None, mode="start", seconds=1.0):
    """
    Adjust timestamps in an Emlid Survey CSV by a specified time delta (in seconds).

    mode options:
      "start" → subtract {seconds} from 'Averaging start' (default)
      "end"   → add {seconds} to 'Averaging end'
      "both"  → do both adjustments
    """

    # Determine default output filename based on mode and seconds
    if output_csv is None:
        base, ext = os.path.splitext(input_csv)
        sign = f"+{seconds}" if seconds > 0 else f"{seconds}"
        if mode == "start":
            suffix = f"_AveragingStart{sign.replace('+', '-') }sec"
        elif mode == "end":
            suffix = f"_AveragingEnd+{seconds}sec"
        elif mode == "both":
            suffix = f"_AveragingStart-{seconds}sec_AveragingEnd+{seconds}sec"
        else:
            raise ValueError("mode must be 'start', 'end', or 'both'")
        output_csv = f"{base}{suffix}{ext}"

    df = pd.read_csv(input_csv)

    def adjust_column(df, col, delta):
        if col not in df.columns:
            print(f"⚠️  Skipping: column '{col}' not found.")
            return df

        # Prepare datetime parsing (handle timezone-aware Emlid format)
        series = df[col].astype(str).str.replace(" UTC", "", regex=False)
        dt = pd.to_datetime(series, utc=False, errors="coerce")

        # Apply delta
        dt = dt + delta

        # Reformat to Emlid-style string with fractional seconds + UTC offset
        df[col] = (
            dt.dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            .str.rstrip("0")
            .str.rstrip(".")
            + " UTC"
            + dt.dt.strftime("%z").str.replace(r"(\d{2})(\d{2})", r"\1:\2", regex=True)
        )
        return df

    delta = timedelta(seconds=abs(seconds))

    if mode == "start":
        df = adjust_column(df, "Averaging start", -delta)
    elif mode == "end":
        df = adjust_column(df, "Averaging end", delta)
    elif mode == "both":
        df = adjust_column(df, "Averaging start", -delta)
        df = adjust_column(df, "Averaging end", delta)
    else:
        raise ValueError("mode must be 'start', 'end', or 'both'")

    df.to_csv(output_csv, index=False)
    print(f"✅ Saved adjusted CSV to: {output_csv}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Adjust Emlid Survey CSV timestamps by a specified time delta (timezone-aware)."
    )
    parser.add_argument("input_csv", help="Path to input Emlid Survey CSV")
    parser.add_argument(
        "output_csv",
        nargs="?",
        help="Optional custom output path (auto-generated if omitted)",
    )
    parser.add_argument(
        "--mode",
        choices=["start", "end", "both"],
        default="start",
        help="Which timestamps to adjust (default: start)",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=1.0,
        help="Number of seconds to shift timestamps (default: 1.0). "
             "Positive values add to end / subtract from start.",
    )

    args = parser.parse_args()
    adjust_emlid_csv(args.input_csv, args.output_csv, mode=args.mode, seconds=args.seconds)
