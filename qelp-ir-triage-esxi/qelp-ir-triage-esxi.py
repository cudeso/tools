#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Plot ESXi activity timelines and extract Bash commands")
    p.add_argument(
        "--files", "-f", nargs="+", required=True,
        help="Timeline CSV files"
    )
    p.add_argument(
        "--output", "-o", required=True,
        help="Output directory"
    )
    return p.parse_args()


def extract_hostname(source_csv):
    import re
    m = re.search(r'/([^/]+)\.zip_results', source_csv)
    if m:
        return m.group(1)
    m = re.search(r'/([^/]+)\.tgz_results', source_csv)
    if m:
        return m.group(1)
    return "unknown"


def load_data(csv_files):
    frames = []
    for path in csv_files:
        df = pd.read_csv(path, header=None, engine="python", dtype=str, na_filter=False)
        ts = pd.to_datetime(df.iloc[:, 0], errors="coerce")
        desc = df.iloc[:, 1].astype(str) if df.shape[1] > 1 else ""
        action = df.iloc[:, 2].str.strip() if df.shape[1] > 2 else ""

        source_csv = str(path)
        hostname = extract_hostname(source_csv)
        frames.append(pd.DataFrame({
            "Timestamp": ts,
            "Description": desc,
            "Action": action,
            "Source CSV": source_csv,
            "Hostname": hostname
        }))
    return pd.concat(frames, ignore_index=True).dropna(subset=["Timestamp"])


def export_table(df, outdir, filename, table_title):
    csv_path = outdir / filename
    df.to_csv(csv_path, index=False)
    print(f"\n{table_title}:")
    print(df.to_markdown(index=False))
    print(f"\nTable saved to {csv_path}\n")


def plot_action_logon(df, outpath):
    df_logon = df[df["Action"].str.casefold() == "logon"].copy()
    t0, t1 = df_logon["Timestamp"].min(), df_logon["Timestamp"].max()
    plt.figure(figsize=(12, 2))
    plt.scatter(df_logon["Timestamp"], [0]*len(df_logon), s=20, alpha=0.6)
    ax = plt.gca()
    ax.set_xlim(t0, t1)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
    plt.yticks([])
    plt.xlabel("Date")
    plt.title("Logon events")
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

    df_logon_table = df_logon.copy()
    df_logon_table["Description"] = df_logon_table["Description"].str.slice(0, 50)
    df_logon_table = df_logon_table[["Timestamp", "Description", "Action", "Hostname"]].sort_values("Timestamp")
    export_table(
        df_logon_table,
        outpath.parent,
        "timeline_action_logon.csv",
        "All 'Action Logon' entries"
    )


def plot_by_event_type(df, outpath):
    df["Date"] = df["Timestamp"].dt.floor("d")

    def classify(desc):
        d = desc or ""
        if re.search(r'SSH access has been disabled|SSH login disabled|ESXi shell login disabled', d, re.IGNORECASE):
            return 'ssh_disabled'
        if re.search(r'SSH access has been enabled|SSH login enabled|ESXi shell login enabled', d, re.IGNORECASE):
            return 'ssh_enabled'
        if re.search(r'User \w+@\d+\.\d+\.\d+\.\d+ logged in as VMware-client', d, re.IGNORECASE):
            return 'vmware_client'
        if re.search(r'Accepted keyboard-interactive/pam|Connection from', d, re.IGNORECASE):
            return 'ssh_connection'
        if re.search(r'Accepted password for', d, re.IGNORECASE):
            return 'accepted_password'
        return None

    df["EventType"] = df["Description"].apply(classify)
    df_evt = df[df["EventType"].notna()].copy()

    lanes = ['ssh_connection', 'ssh_disabled', 'ssh_enabled', 'vmware_client', 'accepted_password']
    spacing = 1.5
    y_pos = {etype: i*spacing for i, etype in enumerate(lanes)}
    t0, t1 = df_evt["Date"].min(), df_evt["Date"].max()

    plt.figure(figsize=(12, spacing*len(lanes)))
    for etype, grp in df_evt.groupby("EventType"):
        plt.scatter(
            grp["Date"], [y_pos[etype]]*len(grp), s=50, alpha=0.7, label=etype, edgecolors='k'
        )

    ax = plt.gca()
    ax.set_xlim(t0, t1)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

    plt.yticks([y_pos[e] for e in lanes], lanes)
    plt.xlabel("Date")
    plt.title("Logon events by type")
    plt.tight_layout()
    plt.legend(title="Event Type", loc="upper left",
               bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()

    df_evt_sorted = df_evt[["Timestamp", "Description", "Action", "EventType", "Hostname"]].sort_values("Timestamp")
    export_table(
        df_evt_sorted,
        outpath.parent,
        "timeline_event_type.csv",
        "All logon entries by event type"
    )


def plot_users(df, outpath):
    df_logon = df[df["Action"].str.casefold() == "logon"].copy()

    records = []
    for _, row in df_logon.iterrows():
        d = row["Description"]
        m = re.search(r'User (\w+)@([\d\.]+) logged in as VMware-client', d)
        if m:
            user = f"{m.group(1)} (vmware-client)"
            ip = m.group(2)
        else:
            m2 = re.search(r'Accepted [^ ]+ for ([^ ]+) from ([\d\.]+) port', d)
            if m2:
                user, ip = m2.group(1), m2.group(2)
            else:
                continue
        records.append((row["Timestamp"], user, ip, row["Hostname"]))

    df2 = pd.DataFrame(records, columns=["Timestamp", "User", "IP", "Hostname"])
    df2["Date"] = df2["Timestamp"].dt.floor("d")
    user_counts = df2.groupby(["Date", "User"]).size().reset_index(name="Count")
    ip_counts = df2.groupby(["Date", "IP"]).size().reset_index(name="Count")

    users = sorted(user_counts["User"].unique())
    ips = sorted(ip_counts["IP"].unique())
    lanes = users + [""] + ips
    spacing = 1.5
    y_pos = {name: i*spacing for i, name in enumerate(lanes)}

    t0, t1 = df2["Date"].min(), df2["Date"].max()
    maxc = max(user_counts["Count"].max(), ip_counts["Count"].max())
    scale = 200.0/maxc if maxc > 0 else 20

    plt.figure(figsize=(14, spacing*len(lanes)))
    for user in users:
        grp = user_counts[user_counts["User"] == user]
        plt.scatter(grp["Date"], [y_pos[user]]*len(grp),
                    s=grp["Count"]*scale+10, alpha=0.7,
                    edgecolors='k', label=user)
    for ip in ips:
        grp = ip_counts[ip_counts["IP"] == ip]
        plt.scatter(grp["Date"], [y_pos[ip]]*len(grp),
                    s=grp["Count"]*scale+10, alpha=0.7,
                    edgecolors='k', label=ip)

    ax = plt.gca()
    ax.set_xlim(t0, t1)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

    plt.yticks([y_pos[n] for n in lanes], lanes)
    plt.xlabel("Date")
    plt.title("Logon users & IPs")
    plt.tight_layout()
    plt.legend(title="User / IP", loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()

    df2_sorted = df2[["Timestamp", "User", "IP", "Hostname"]].sort_values("Timestamp")
    export_table(
        df2_sorted,
        outpath.parent,
        "timeline_logon_users_ips.csv",
        "All logon users and IPs"
    )


def plot_activity(df, outpath):
    df["Date"] = df["Timestamp"].dt.floor("d")
    lanes = ["Bash_activity", "Logon", "User_activity"]
    spacing = 1.5
    y_pos = {atype: i*spacing for i, atype in enumerate(lanes)}
    counts = (
        df[df["Action"].isin(lanes)]
          .groupby(["Date", "Action", "Hostname"])
          .size()
          .reset_index(name="Count")
    )
    t0, t1 = counts["Date"].min(), counts["Date"].max()
    maxc = counts["Count"].max()
    scale = 200.0/maxc if maxc > 0 else 20

    plt.figure(figsize=(12, spacing*len(lanes)))
    for action, grp in counts.groupby("Action"):
        plt.scatter(
            grp["Date"], [y_pos[action]]*len(grp),
            s=grp["Count"]*scale+10, alpha=0.7,
            edgecolors='k', label=action
        )

    ax = plt.gca()
    ax.set_xlim(t0, t1)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

    plt.yticks([y_pos[a] for a in lanes], lanes)
    plt.xlabel("Date")
    plt.title("Activity by action")
    plt.tight_layout()
    plt.legend(title="Action", loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()

    export_table(
        counts[["Date", "Action", "Count", "Hostname"]],
        outpath.parent,
        "timeline_activity.csv",
        "Activity by action and date"
    )


def dive_logs(df, outdir):
    df_bash = df[df["Action"] == "Bash_activity"].copy()
    exclude = {
        "ESXi Shell available",
        "ESXi shell login enabled",
        "SSH login enabled",
        "SSH login disabled",
        "Interactive shell session started"
    }
    df_bash = df_bash[~df_bash["Description"].isin(exclude)]


    def simplify(desc):
        parts = desc.split()
        if not parts:
            return ""
        if parts[0] == "esxcli" and len(parts) > 1:
            return "esxcli " + parts[1]
        return parts[0]
    df_bash["Command"] = df_bash["Description"].apply(simplify)
    table1 = (
        df_bash.groupby(["Command", "Hostname"])
               .size()
               .reset_index(name="Count")
               .sort_values("Count", ascending=False)
               .reset_index(drop=True)
    )
    export_table(
        table1,
        outdir,
        "summary_bash_activity_commands.csv",
        "Bash activity commands (excluding standard messages)"
    )

    pattern = re.compile(r'\b(?:curl|wget|nc|tcpdump|ssh)\b', re.IGNORECASE)
    df_net = df_bash[df_bash["Description"].str.contains(pattern)]
    table2 = (
        df_net.groupby(["Description", "Hostname"])
        .size()
        .reset_index(name="Count")
        .rename(columns={"Description": "CommandLine"})
        .sort_values("CommandLine")
    )
    export_table(
        table2,
        outdir,
        "summary_network_tool_commands.csv",
        "Network tool commands in Bash activity (curl, wget, nc, tcpdump, ssh)"
    )

    df_add = df[df["Description"].str.contains(r'esxcli system account add', case=False)]
    df_add["NewUser"] = df_add["Description"].str.extract(r'-i="([^"]+)"', expand=False)
    table3 = (
        df_add.groupby(["NewUser", "Hostname"])
        .size()
        .reset_index(name="Count")
        .rename(columns={"NewUser": "User"})
    )
    export_table(
        table3,
        outdir,
        "summary_new_users_added.csv",
        "New users added via 'esxcli system account add'"
    )


def combine_timeline(df, outdir):
    combined = df.copy()
    if 'Source CSV' in combined.columns:
        combined['source_file'] = combined['Source CSV']
    else:
        combined['source_file'] = 'unknown'

    ts_strings = combined['Timestamp'].astype(str).str.replace(r'Z$', '+00:00', regex=True)
    try:
        combined['Timestamp'] = pd.to_datetime(
            ts_strings,
            format='ISO8601',
            utc=True,
            errors='raise'
        )
    except Exception as e:
        print(f"Combining timelines: Error parsing 'Timestamp' values: {e}", file=sys.stderr)

    other_cols = [col for col in combined.columns if col not in ['Timestamp', 'source_file']]
    combined = combined[['Timestamp', 'source_file'] + other_cols]

    combined = combined.sort_values('Timestamp')

    out_csv = Path(outdir) / "combined_timeline.csv"
    try:
        combined.to_csv(out_csv, index=False)
        print(f"Combined timeline written to '{out_csv}' sorted by Timestamp.")
    except Exception as e:
        print(f"Combining timelines: Error writing output file '{out_csv}': {e}", file=sys.stderr)


def main():
    args = parse_args()
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_data(args.files)
    if df.empty:
        print("No valid timestamped rows found.", file=sys.stderr)
        sys.exit(1)

    plot_action_logon(df,    outdir/"timeline_action_logon.png")
    plot_by_event_type(df,   outdir/"timeline_event_type.png")
    plot_users(df,           outdir/"timeline_logon_users_ips.png")
    plot_activity(df,        outdir/"timeline_activity.png")
    dive_logs(df, outdir)
    combine_timeline(df, outdir)    

    print("\n==== Global Timeline Stats ====")
    print(f"First entry: {df['Timestamp'].min()}")
    print(f"Last entry: {df['Timestamp'].max()}")
    print(f"Number of entries: {len(df)}")
    print(f"Number of identified hosts: {df['Hostname'].nunique()}")

    print("Output written to:", outdir)

if __name__ == "__main__":
    main()
