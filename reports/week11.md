---

team: TerpLoad
week: 11
date: 2026-08-10

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
  metric: Corrected labels and model retraining
  value: Weak labels were audited, confirmed wrong labels were fixed, and TF-IDF / DistilBERT were retrained on corrected data
  previous: Week 10 labeled reviews added, TF-IDF evaluation updated, and low-evidence warnings added

---

## Shipped this week

* Audited weak labels that were marked as positive but contradicted the review text
* Hand-checked flagged reviews before changing labels
* Fixed 493 confirmed-wrong labels in the master labeled CSV
* Regenerated `data/splits/train.csv`, `data/splits/val.csv`, and `data/splits/test.csv`
* Retrained TF-IDF on the corrected labels
* Updated and retrained DistilBERT on the corrected labels
* Added class weighting to DistilBERT
* Added a fixed random seed and main guard to `train_distilbert.py`
* Added `requirements.txt`
* Regenerated `data/course_workload_signals.json`

## User / validation learning

The main learning this week is that some weak labels needed correction before model results could be trusted.

After fixing confirmed-wrong labels, both models were retrained on cleaner data. DistilBERT performed better than TF-IDF on the corrected dataset.

The current TerpLoad flow is:

* cleaned PlanetTerp reviews
* corrected weak labels
* train / validation / test splits
* TF-IDF and DistilBERT training
* course workload signals
* CLI / Streamlit report

## Metrics snapshot

* Confirmed-wrong labels fixed: 493
* TF-IDF subset accuracy: 0.537
* TF-IDF macro F1: 0.652
* TF-IDF micro F1: 0.667
* DistilBERT subset accuracy: 0.661
* DistilBERT macro F1: 0.725
* DistilBERT micro F1: 0.723
* `requirements.txt` added: yes

## Challenges / blockers

* The audit focused on labels incorrectly marked as `1`

## Next week's goal

* Update `docs/error_analysis.md`
* Prepare final model results for the report/demo

## Individual contributions

- Moataz Abdelaziz (Product): Audited weak labels, fixed confirmed-wrong labels, regenerated splits, retrained TF-IDF and DistilBERT, updated DistilBERT training code, added requirements. (evidence: [issue #48](https://github.com/moatazsaad/msml641-project/issues/48), [PR #49](https://github.com/moatazsaad/msml641-project/pull/49))
- Abhiram Metuku (Data&Eval): To (evidence: [issue #46](https://github.com/moatazsaad/msml641-project/issues/46), [PR #47](https://github.com/moatazsaad/msml641-project/pull/47))
* Sriram Vema (Engineering): To  (evidence: issue #X, PR #Y)

