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
  metric: MVP label alignment
  value: Docs and baseline logic aligned to four first-version workload labels
  previous: Initial labeled review sample created

---

## Shipped this week

* Aligned the MVP documentation with the four first-version workload labels. (evidence: issue #X, PR #Y)
* Simplified the baseline risk logic to use the same four labels. (evidence: issue #X, PR #Y)

## User / validation learning

The first version should stay focused on the clearest workload signals from interviews and review examples:

* project_heavy
* exam_heavy
* homework_heavy
* time_consuming

Extra signals like professor dependence, harsh grading, self-learning, lab-heavy workload, and writing-heavy workload are useful, but we are keeping them as future modifiers for now.

## Metrics snapshot

* First-version workload labels: 4
* Docs aligned with four-label MVP: yes
* Baseline risk logic aligned with four-label MVP: yes

## Challenges / blockers

* We still need more real PlanetTerp review text.
* We need a larger labeled dataset before training a model.

## Next week's goal

* Collect and clean more PlanetTerp reviews.
* Prepare the data for a simple baseline classifier.

## Individual contributions

* Moataz Abdelaziz (Product): Aligned MVP documentation and baseline risk logic with the four-label first model. (evidence: issue 15, PR #16)
* Abhiram Metuku (Data&Eval): To be updated after teammate input. (evidence: ...)
* Sriram Vema (Engineering): Defined input columns for training, created src/train_tfidf_classifier.py skeleton and src/workload_signal_baseline.py

## Lean canvas changes

* The MVP scope is now cleaner: the first model uses four workload labels only.
* Extra workload signals are treated as future modifiers instead of first-version labels.
