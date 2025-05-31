```
flowchart LR
  %% Define ESX01.zip and its logs
  subgraph ESX01.zip
    A1[auth.log]
    A2[hostd.log]
    A3[shell.log]
    A4[vobd.log]
  end

  %% Define ESX02.zip and its logs
  subgraph ESX02.zip
    B1[auth.log]
    B2[hostd.log]
    B3[shell.log]
    B4[vobd.log]
  end

  %% Point both ZIP archives to QELP
  ESX01.zip --> QELP[QELP]
  ESX02.zip --> QELP

  %% QELP produces per-host Timeline.csv
  QELP --> T1[ESX01 Timeline.csv]
  QELP --> T2[ESX02 Timeline.csv]

  %% All Timelines feed into qelp-ir-triage-esxi
  T1 --> TRIAGE[qelp-ir-triage-esxi]
  T2 --> TRIAGE

  %% qelp-ir-triage-esxi produces various output categories
  TRIAGE --> Logons[Logons]
  TRIAGE --> Remote[Remote Activity]
  TRIAGE --> Bash[Bash Activity]
  TRIAGE --> Net[Network Commands]
  TRIAGE --> Users[New Users]

  %% Each category points to its CSV/PNG
  Logons --> Logons_CSV[Logons.csv]
  Logons --> Logons_PNG[Logons.png]

  Remote --> Remote_CSV[RemoteActivity.csv]
  Remote --> Remote_PNG[RemoteActivity.png]

  Bash --> Bash_CSV[BashActivity.csv]

  Net --> Net_CSV[NetworkCommands.csv]

  Users --> Users_CSV[NewUsers.csv]

  %% Outputs feed into the Incident Response grouping
  subgraph "Incident Response"
    Quick[Quick Triage]
    IR[Incident Response Report]
  end

  %% Link all CSVs/PNGs to Quick Triage and Incident Response Report
  Logons_CSV --> Quick
  Logons_PNG --> Quick
  Remote_CSV --> Quick
  Remote_PNG --> Quick
  Bash_CSV --> Quick
  Net_CSV --> Quick
  Users_CSV --> Quick

  Logons_CSV --> IR
  Logons_PNG --> IR
  Remote_CSV --> IR
  Remote_PNG --> IR
  Bash_CSV --> IR
  Net_CSV --> IR
  Users_CSV --> IR

  %% Style definitions
  style IR fill:#cce5ff,stroke:#333,stroke-width:1px
  style Quick fill:#e0ccff,stroke:#333,stroke-width:1px
```