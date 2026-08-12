---

team: TerpLoad
week: 11
date: 2026-08-12

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

* Audited and corrected weak labels, fixing 493 confirmed-wrong labels
* Regenerated train/validation/test splits and retrained TF-IDF and DistilBERT
* Selected DistilBERT as the final model based on stronger evaluation results
* Validated thresholds and course-level workload aggregation
* Added low-evidence handling and historical grade context
* Verified that grades do not affect workload signals or schedule risk
* Integrated final DistilBERT inference into the backend
* Added live review fetching for new courses, caching, and backend/API testing
* Regenerated course workload signals and updated project requirements

## User / validation learning

The main learning this week is that some weak labels needed correction before model results could be trusted.

After fixing confirmed-wrong labels, both models were retrained on cleaner data. DistilBERT performed better than TF-IDF on the corrected dataset.

The current TerpLoad flow is:

* cleaned PlanetTerp reviews
* corrected weak labels
* train / validation / test splits
* TF-IDF and DistilBERT training/evaluation
* saved DistilBERT inference
* course workload aggregation
* low-evidence handling and grade context
* schedule-risk calculation
* CLI / Streamlit report

## Metrics snapshot

* Confirmed-wrong labels fixed: 493
* Test set size: 760 reviews
* TF-IDF subset accuracy: 0.537
* TF-IDF macro F1: 0.652
* TF-IDF micro F1: 0.667
* DistilBERT subset accuracy: 0.647
* DistilBERT macro F1: 0.739
* DistilBERT micro F1: 0.738
* Final model selected: DistilBERT

## Challenges / blockers

* The audit focused on labels incorrectly marked as `1`
* Courses with few reviews have less reliable workload estimates
* Long reviews may be truncated by DistilBERT’s input limit

## Next week's goal

* Update `docs/error_analysis.md`
* Prepare final model results for the report/demo and presentation

## Individual contributions

* Moataz Abdelaziz (Product): Audited weak labels, fixed confirmed-wrong labels, regenerated splits, retrained TF-IDF and DistilBERT, updated DistilBERT training code, added requirements. (evidence: [issue #48](https://github.com/moatazsaad/msml641-project/issues/48), [PR #49](https://github.com/moatazsaad/msml641-project/pull/49))
* Abhiram Metuku (Data&Eval): Compared final TF-IDF and DistilBERT results, validated model thresholds, tested course-level workload aggregation, implemented low-evidence handling and grade-context logic, and added evaluation/tests for schedule-risk behavior. (evidence: [issue #46](https://github.com/moatazsaad/msml641-project/issues/46), [PR #47](https://github.com/moatazsaad/msml641-project/pull/47))
* Sriram Vema (Engineering): Final DistilBERT integration, Live new-course review fetching, Saved-model inference, Caching/backend servic, Backend/API testing
 (evidence: [PR #50](https://github.com/moatazsaad/msml641-project/pull/50))

