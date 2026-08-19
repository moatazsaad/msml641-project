# TerpLoad production architecture

```mermaid
flowchart LR
    PT[PlanetTerp reviews] --> RAW[Raw response cache]
    RAW --> DB[Saved DistilBERT inference]
    DB --> AGG[Course-level aggregation]
    AGG --> PC[Persistent profile cache]
    PC --> RULES[Schedule-risk rules]
    RULES --> UI[Streamlit UI]

    GRADES[Historical grade records] --> CONTEXT[Grade context]
    CONTEXT -. separate context branch .-> UI
```

Workload risk is derived only from PlanetTerp review text classified by the
saved DistilBERT model. Historical grades are contextual information and do
not feed the workload classifier or schedule-risk score.
