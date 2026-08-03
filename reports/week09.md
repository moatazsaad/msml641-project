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
  value: TF-IDF course signals connected to the CLI report, with initial model comparison and error analysis
  previous: Simple report CLI created for user testing

---

## Shipped this week

* Added `src/predict_course_signals.py` to generate course-level workload signals from the TF-IDF baseline
* Created `data/course_workload_signals.json` with predicted workload signals for collected courses
* Updated `src/simple_report_cli.py` so the CLI uses generated course signals instead of hardcoded sample data
* Added tests for the simple report CLI in `src/test_simple_report_cli.py`

## User / validation learning

The report is more useful when it is connected to real review-based signals instead of manually typed sample data. 10 additional people said the simple student facing report seems descriptive enough to make a difference in their decision making. within next 2 weeks need to have proper functionality.

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
* DistilBERT experiment completed: yes
* Model mistakes reviewed: 10


## Challenges / blockers

* The labeled data is still small and imbalanced
* Some labels have fewer positive examples
* The current model is a baseline, not the final model
* More labeled data is needed to improve predictions

## Next week's goal

* Aggregate final prediction outputs into course-level workload profiles.
* Add risk modifiers as descriptive context.
* Add grade fallback for courses with limited review evidence.
* Validate several generated course reports manually.
* Prepare the report output for the final demo interface.

## Individual contributions

* Moataz Abdelaziz (Product): Connected the TF-IDF course signals to the CLI report, generated course workload signals and added CLI tests. (evidence: issue #33, PR #34)
* Abhiram Metuku (Data&Eval): Reviewed model mistakes and wrote Week 9 error analysis focused on ambiguous workload signals, fair and heavy reviews, and model limitations. (evidence: issue #35, PR #38)[PR #38](https://github.com/moatazsaad/msml641-project/pull/39))
* Sriram Vema (Engineering): Continued baseline/modeling pipeline work. (evidence: PR #37)

## Lean canvas changes

* The MVP is moving from a sample report flow toward a baseline model-driven report flow
