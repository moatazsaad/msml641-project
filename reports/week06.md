---

team: TerpLoad
week: 06
date: 2026-07-08
members:

* name: Moataz Abdelaziz
  github: "@moatazsaad"
  hat: Product
* name: Abhiram Metuku
  github: "@abhimet"
  hat: "Data&Eval"
* name: Sriram Vema
  github: "@sriramvema"
  hat: Engineering
  north_star:
  metric:End-to-end pilot labeling completion
  value: Docs and baseline logic aligned to four first-version workload labels,30 of 30 pilot reviews received candidate labels
  previous: Initial labeled review sample created

---

## Shipped this week

* Aligned the MVP documentation with the four first-version workload labels and modified risk rules. (evidence: issue #15, PR #16)
* Collected and cleaned 255 PlanetTerp reviews, created a 30-review pilot, generated LLM-assisted candidate labels(need to be audited and what counts for a specific label), and added the merge workflow
* Verified `risk_rules.py`, added the keyword baseline, created the TF-IDF training skeleton, and defined the training input/output schema

## User / validation learning

The first version should stay focused on the clearest workload signals from interviews and review examples:

* project_heavy
* exam_heavy
* homework_heavy
* time_consuming

Extra signals like professor dependence, harsh grading, self-learning, lab-heavy workload, and writing-heavy workload are useful, but we are keeping them as future modifiers for now, not specifically first model targets.(they are in labels though)

## Metrics snapshot

* First-version workload labels: 4
* Docs aligned with four-label MVP: yes
* Baseline risk logic aligned with four-label MVP: yes
* Courses with reviews: 7
* Cleaned reviews: 255
* Pilot reviews labeled: 30
* Core labels: 4
* Supporting modifiers: 3
 

## Challenges / blockers

* Review coverage is uneven across courses.
* MSML606 has no review evidence.
* Candidate labels still need a small human audit.
* More weakly labeled data is needed before meaningful training.


## Next week's goal

* Audit a small subset of the 30 pilot reviews.
* Refine the labeling guidelines.
* Expand the weakly labeled dataset.
* Prepare the first baseline training run.
* Finalize how course signals connect to the schedule-risk report.

## Individual contributions

* Moataz Abdelaziz (Product): Aligned MVP documentation and baseline risk logic with the four-label first model. (evidence: issue 15, PR #16)
* Abhiram Metuku (Data&Eval): Collected and cleaned the PlanetTerp data, created the 30-review pilot, defined the labels and modifiers, generated candidate labels, and built the merge workflow. (evidence: issue 18, PR #19)
* Sriram Vema (Engineering): Defined input columns for training, created src/train_tfidf_classifier.py skeleton and src/workload_signal_baseline.py

## Lean canvas changes

* The MVP stays focused on four core workload labels.
* Full reviews are the first model input.
* Supporting modifiers are kept for explanation and future expansion.
* Courses with no review evidence will show a limited-evidence warning.
