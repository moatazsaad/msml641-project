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
- Created a 64-review weak-labeled dataset for first baseline experiments.(evidence: issue #26, PR #27)
- Added a weakly labeled csv file with four core workload labels and descriptive modifiers.(evidence: issue #26, PR #27)



## User / validation learning

The next thing to test is whether students understand the risk level and reasons before the final model is ready.

## Metrics snapshot

- Simple report CLI: created
- User testing notes: created
- Risk levels: Low, Medium, High
- Final trained model: not completed yet

  
- Raw PlanetTerp reviews collected: about 903
- Cleaned reviews available: 255
- Pilot LLM-labeled reviews: 30
- Week 8 weak-labeled reviews: 64
- Core workload labels: 4
- Descriptive modifiers: 4

## Challenges / blockers

- The CLI uses sample workload signals not final model predictions.
- The report wording still needs some more student feedback.
- The TF-IDF model is not fully connected yet.
- The full end-to-end flow is not complete yet.


## Next week's goal
- Some reviews focus on professor style or grading rather than direct workload.
- MSML606 had no cleaned reviews available in the current dataset.
- project_heavy and homework_heavy have fewer positive examples than exam_heavy and time_consuming.


## Individual contributions

- **Moataz Abdelaziz  (Product):** Built the simple report CLI and added user testing notes. (evidence: issue #29, PR #30)
- **Abhiram Metuku (Data&Eval):**  Created the Week 8 review sample, weak-labeled dataset, label distribution, and labeling notes. (evidence: issue #26, PR #27)
- **Sriram Vema (Engineering):**  Run Keyword and TF IDF baselines, generate results (evidence: PR #32)


