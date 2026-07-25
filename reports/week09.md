---

team: TerpLoad
week: 09
date: 2026-07-29

members:
- name: Moataz Abdelaziz
  github: "@moatazsaad"
  hat: Product
- name: Abhiram Metuku
  github: "@abhimet"
  hat: "Data&Eval"
- name: Sriram Vema
  github: "@sriramvema"
  hat: Engineering

north_star:
  metric: End-to-end baseline report flow
  value: TF-IDF course signals connected to the CLI report
  previous: Simple report CLI created for user testing

---

## Shipped this week

* Added `src/predict_course_signals.py` to generate course-level workload signals from the TF-IDF baseline
* Created `data/course_workload_signals.json` with predicted workload signals for collected courses
* Updated `src/simple_report_cli.py` so the CLI uses generated course signals instead of hardcoded sample data
* Added tests for the simple report CLI in `src/test_simple_report_cli.py`

## User / validation learning

The report is more useful when it is connected to real review-based signals instead of manually typed sample data.

The current TerpLoad flow is:

* labeled reviews
* TF-IDF baseline
* course workload signals
* risk rules
* student-facing CLI report

## Metrics snapshot

* Courses with generated workload signals: 7
* CLI tests added: 5
* Risk-rule tests still passing: 5
* TF-IDF baseline connected to CLI: yes
* Final trained model: not completed yet

## Challenges / blockers

* The labeled data is still small and imbalanced
* Some labels have fewer positive examples
* The current model is a baseline, not the final model
* More labeled data is needed to improve predictions

## Next week's goal

* Add more labeled review data
* Improve model evaluation
* Keep testing the CLI report with realistic course combinations

## Individual contributions

* Moataz Abdelaziz (Product): Connected the TF-IDF course signals to the CLI report, generated course workload signals and added CLI tests. (evidence: issue #33, PR #Y)
* Abhiram Metuku (Data&Eval): Continued labeling and evaluation work. (evidence: issue #X, PR #Y)
* Sriram Vema (Engineering): Continued baseline/modeling pipeline work. (evidence: issue #X, PR #Y)

## Lean canvas changes

* The MVP is moving from a sample report flow toward a baseline model-driven report flow