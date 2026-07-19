---
team: TerpLoad
week: 08
date: 2026-07-22

members:
  - name: Moataz Abdelaziz
    github: "@moatazsaad"
    hat: Product

  - name: Abhiram Metuku
    github: "@abhimet"
    hat: Data & Evaluation

  - name: Sriram Vema
    github: "@sriramvema"
    hat: Engineering

north_star:
  metric: User-testable report flow
  value: Simple CLI prototype created
  previous: Midterm presentation prepared
---

## Shipped this week

- Added a simple command-line prototype where a student enters planned courses and receives a Low, Medium, or High workload-risk report. (evidence: issue #29, PR #30)
- Used the existing `risk_rules.py` logic with sample workload signals to test the report flow. (evidence: issue #29, PR #30)
- Added short user testing notes for checking if the report is clear and useful. (evidence: issue #29, PR #30)

## User / validation learning

The next thing to test is whether students understand the risk level and reasons before the final model is ready.

## Metrics snapshot

- Simple report CLI: created
- User testing notes: created
- Risk levels: Low, Medium, High
- Final trained model: not completed yet

## Challenges / blockers

- The CLI uses sample workload signals not final model predictions
- The report wording still needs student feedback


## Individual contributions

- **Moataz Abdelaziz — Product:** Built the simple report CLI and added user testing notes. (evidence: issue #29, PR #30)
- **Abhiram Metuku — Data & Evaluation:** Continued labeling and evaluation work. (evidence: issue #29, PR #Y)
- **Sriram Vema — Engineering:** Continued baseline/modeling pipeline work. (evidence: issue #29, PR #Y)

