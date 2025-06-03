#!/usr/bin/env python3
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def parse_args():
    parser = argparse.ArgumentParser(
        description="Read a Speedtest CSV and plot download/upload over time."
    )
    parser.add_argument(
        "csv_file",
        help="Path to CSV with speedtest results"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    csv_path = args.csv_file

    if not os.path.isfile(csv_path):
        print(f"Error: '{csv_path}' not found or is not a file.")
        return

    df = pd.read_csv(csv_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    df = df.sort_values('Timestamp')
    df['Download_Mbps'] = df['Download'] / 1e6
    df['Upload_Mbps']   = df['Upload']   / 1e6
    dl_max_row = df.loc[df['Download_Mbps'].idxmax()]
    dl_min_row = df.loc[df['Download_Mbps'].idxmin()]
    ul_max_row = df.loc[df['Upload_Mbps'].idxmax()]
    ul_min_row = df.loc[df['Upload_Mbps'].idxmin()]

    dl_max_val = dl_max_row['Download_Mbps']
    dl_max_time = dl_max_row['Timestamp']
    dl_min_val = dl_min_row['Download_Mbps']
    dl_min_time = dl_min_row['Timestamp']

    ul_max_val = ul_max_row['Upload_Mbps']
    ul_max_time = ul_max_row['Timestamp']
    ul_min_val = ul_min_row['Upload_Mbps']
    ul_min_time = ul_min_row['Timestamp']

    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    ax.plot(
        df['Timestamp'],
        df['Download_Mbps'],
        label='Download (Mbps)',
        marker='o',
        linestyle='-'
    )
    ax.plot(
        df['Timestamp'],
        df['Upload_Mbps'],
        label='Upload (Mbps)',
        marker='o',
        linestyle='-'
    )

    stats_text = (
        f"Download max: {dl_max_val:.2f} Mbps at {dl_max_time:%Y-%m-%d %H:%M}\n"
        f"Download min: {dl_min_val:.2f} Mbps at {dl_min_time:%Y-%m-%d %H:%M}\n\n"
        f"Upload max:   {ul_max_val:.2f} Mbps at {ul_max_time:%Y-%m-%d %H:%M}\n"
        f"Upload min:   {ul_min_val:.2f} Mbps at {ul_min_time:%Y-%m-%d %H:%M}"
    )
    ax.text(
        0.02, 0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize="small",
        va='top',
        ha='left',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.6, edgecolor='gray')
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Speed (Mbps)")
    ax.set_title("Internet speed tests")

    start_date = df['Timestamp'].iloc[0]
    end_date   = df['Timestamp'].iloc[-1]
    ax.set_xlim(start_date, end_date)

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.legend(
        loc='center left',
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0
    )

    plt.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    output_png = os.path.splitext(os.path.basename(csv_path))[0] + ".png"
    plt.savefig(output_png, dpi=150)
    print(f"Plot saved as '{output_png}'")

if __name__ == "__main__":
    main()
