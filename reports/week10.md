---

team: TerpLoad
week: 10
date: 2026-08-05

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
  metric: End-to-end schedule report coverage
  value: Workload signals generated for 109 courses and connected to the Streamlit schedule-risk report
  previous: TF-IDF course signals connected to the CLI report

---

## Shipped this week

* Expanded the weak-labeled review dataset to 5,059 reviews
* Created fixed train, validation, and held-out test splits
* Updated TF-IDF evaluation with 5-fold cross-validation and validation-selected thresholds
* Removed outdated Week 8 and Week 10 dataset dependencies from active Python files
* Regenerated workload signals for 109 courses from the cleaned review corpus
* Added low-evidence warnings for courses with limited review coverage
* Added a Streamlit demo using the same course signals and risk logic as the CLI

## User / validation learning

Adding more labeled reviews expanded the dataset, but the model still struggled with some labels, especially `homework_heavy`.

The current TerpLoad flow is:

* cleaned PlanetTerp reviews
* weak workload labels
* TF-IDF baseline
* course workload signals
* risk rules
* CLI / Streamlit report

## Metrics snapshot

* Full weak-labeled dataset: 5,059 reviews
* Training split: 3,541 reviews
* Validation split: 758 reviews
* Held-out test split: 760 reviews
* Workload labels: 4
* TF-IDF evaluation: 5-fold cross-validation
* Tests passing: 12/12
* Final trained model: not completed yet

## Challenges / blockers

* `project_heavy` appears less frequently than the other workload labels
* `time_consuming` has the weakest current TF-IDF test performance
* Some courses, especially MSML courses, have very few reviews
* The course-level threshold can hide moderate evidence behind a binary `False`
* The current model output still needs final engineering review and integration

## Next week's goal

* Finalize the model and course-signal pipeline
* Investigate unusual course-level workload signals
* Complete the low-evidence and grade fallback experience(planetterp has grade data)
* Conduct final user testing
* Finish deployment and demo preparation

## Individual contributions

* Moataz Abdelaziz (Product): Added Week 10 updates, low-evidence warning, tests, documentation updates, and Streamlit demo. (evidence: issue #42, PR #43)
* Abhiram Metuku (Data&Eval): Expanded and weak-labeled the review dataset, created fixed data splits, updated TF-IDF evaluation, removed outdated dataset paths, and regenerated workload signals for 109 courses. (evidence: issue #39, PR #41)
* Sriram Vema (Engineering):  Retrained on updated dataset, finalized model as distilBERT due to better performance (evidence: PR #45)

## Lean canvas changes

* The MVP should show when review evidence is limited
* Signal strength should not be presented as absolute certainty
* Historical grade information may be shown as secondary context, but it should not determine workload labels
* The final MVP should prioritize a reproducible NLP pipeline and an understandable schedule-risk report
