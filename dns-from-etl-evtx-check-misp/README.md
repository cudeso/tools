# Windows DNS logging

## Windows Server DNS Logging and Diagnostics

Enhanced DNS logging and diagnostics is available in Windows Server 2016 and upwards. You can enable it based on this Microsoft article: [https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn800669(v=ws.11)](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn800669(v=ws.11)). The analytic logs are then written to `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-DNSServer%4Analytical.etl`.

When you open the ETL file in the Windows Event Viewer, you can convert it to an `evtx`.

Because neither the ETL or EVTX allow easy export of specific fields (in this case the DNS query) this Python script extracts the queries, and checks the hostname (query) and the extracted domain (from the query) against MISP.

# Extract domains and hostnames

Update the **MISP credentials** in `check_misp`.

Run the script with the EVTX file as argument. Optionally add a maximum record count to test the script first with a minimal numbers of rows.

```
python parse_dns_evtx.py export.evtx 500
```

The script 
- writes the extracted **DNS records** in a CSV file `dns_events.csv`
- writes the extracted **hostnamess** (queries) in a CSV file `dns_hostnames.csv.csv`
- writes the extracted **domains** in a CSV file `dns_domains.csv`

# Workflow

[![](https://mermaid.ink/img/pako:eNptkDFvwkAMhf-KdVI30qlThkqQMFSCCjUIqiYMp8Qkpybn1OeURsB_r4G2U2862-_zk9_RlFShiU3Ntm9g8VJ40DfNE0YrCOlzBlNv21FcCQuqdxBFj6dMiLEC52HpSqZAe4m2zld0CJESGfIn8t3DL2jbe5T2BLM8Ia8Tgfl6AUIw36xfdzfH2WUxJPnKckA4OGlgNUpDHrKSXS8_suTqP_8StqXAx4A8QkNBvO3wBGmeNFi-g62t80Fg-ZSt_gUr6lShwG2YXs3n-Zad3kyDAGMYWgmXE5NsE3SJmZgOWbFK0zpeuMJIgx0WJtZvhXurRGEKf1apHYSy0ZcmFh5wYpiGujHx3rZBq6GvNNzUWU29--v21r8R_dbnb5UqiUM?type=png)](https://mermaid.live/edit#pako:eNptkDFvwkAMhf-KdVI30qlThkqQMFSCCjUIqiYMp8Qkpybn1OeURsB_r4G2U2862-_zk9_RlFShiU3Ntm9g8VJ40DfNE0YrCOlzBlNv21FcCQuqdxBFj6dMiLEC52HpSqZAe4m2zld0CJESGfIn8t3DL2jbe5T2BLM8Ia8Tgfl6AUIw36xfdzfH2WUxJPnKckA4OGlgNUpDHrKSXS8_suTqP_8StqXAx4A8QkNBvO3wBGmeNFi-g62t80Fg-ZSt_gUr6lShwG2YXs3n-Zad3kyDAGMYWgmXE5NsE3SJmZgOWbFK0zpeuMJIgx0WJtZvhXurRGEKf1apHYSy0ZcmFh5wYpiGujHx3rZBq6GvNNzUWU29--v21r8R_dbnb5UqiUM)

# Sample output

```
    EventID                 TimeCreated         Computer        Source                      QNAME
0       261  2024-12-02 12:04:24.662960  WIN-DEMO   172.16.4.12        M.ROOT-SERVERS.NET.
1       261  2024-12-02 12:04:24.662971  WIN-DEMO   172.16.4.12  win10.ipv6.microsoft.com.
2       259  2024-12-02 12:04:24.662996  WIN-DEMO   172.16.4.12  win10.ipv6.microsoft.com.
3       259  2024-12-02 12:04:24.662998  WIN-DEMO   172.16.4.12        M.ROOT-SERVERS.NET.
4       256  2024-12-02 12:04:26.852987  WIN-DEMO  172.16.4.223        gameplay.intel.com.
..      ...                         ...              ...           ...                        ...
362     259  2024-12-02 12:07:48.570248  WIN-DEMO   172.16.4.12        M.ROOT-SERVERS.NET.
363     261  2024-12-02 12:07:49.476603  WIN-DEMO   172.16.4.12  win10.ipv6.microsoft.com.
364     259  2024-12-02 12:07:49.476618  WIN-DEMO   172.16.4.12  win10.ipv6.microsoft.com.
365     261  2024-12-02 12:07:56.732590  WIN-DEMO   172.16.4.12        M.ROOT-SERVERS.NET.
366     259  2024-12-02 12:07:56.732603  WIN-DEMO   172.16.4.12        M.ROOT-SERVERS.NET.

[367 rows x 5 columns]



Sorted hostnames:
                          Hostname  Count  MISP_Check
               M.ROOT-SERVERS.NET.    123       False
         win10.ipv6.microsoft.com.     63       False
          ctldl.windowsupdate.com.     50       False
            update.googleapis.com.     34       False
                  armmf.adobe.com.     34       False
                   ecs.office.com.     21       False
               gameplay.intel.com.     17       False
v10.vortex-win.data.microsoft.com.     16       False
  settings-win.data.microsoft.com.      9       False



Sorted domains:
           Domain  Count  MISP_Check
 ROOT-SERVERS.NET    123       False
    microsoft.com     88        True
windowsupdate.com     50       False
   googleapis.com     34        True
        adobe.com     34        True
       office.com     21        True
        intel.com     17       False
```