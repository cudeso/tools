---
config:
  layout: dagre
  theme: default
---
flowchart LR
 subgraph Config["Config"]
        CFG["config.py (API keys, URLs, settings)"]
  end
 subgraph Core["Core"]
        Main["main()"]
        RLC["RansomLookClient"]
        Enricher["Enricher"]
        Storage["JsonStorage"]
        Notifier["MattermostNotifier"]
  end
 subgraph External["External"]
        API["RansomLook API"]
        Google["Google Custom Search"]
        OpenAI["OpenAI ChatGPT"]
        MM["Mattermost Webhook"]
        FS["Filesystem (JSON & logs)"]
  end
    CFG --> Main
    Main --> RLC & Enricher & Storage & Notifier
    RLC -- fetch posts --> API
    Enricher -- search snippets --> Google
    Enricher -- LLM prompt --> OpenAI
    Storage -- read/write --> FS
    Notifier -- post messages --> MM
    Main -- load history --> Storage
    Main -- filter new --> Storage
    Main -- save all --> Storage
    Main -- notify --> Notifier
