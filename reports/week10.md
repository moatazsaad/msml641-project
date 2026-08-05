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
  metric: Baseline evaluation and report updates
  value: Week 10 labeled reviews added, TF-IDF evaluation updated, and low-evidence warnings added to the report flow
  previous: TF-IDF course signals connected to the CLI report

---

## Shipped this week

* Added Week 10 weak-labeled reviews
* Updated TF-IDF evaluation to use 5-fold cross-validation
* Added a low-evidence warning for courses with few reviews
* Updated documentation for weak labels and model limitations
* Added tests for the low-evidence warning
* Added a simple Streamlit demo using the same report logic as the CLI

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

* Labeled reviews: 104
* Reviews added this week: 40
* Workload labels: 4
* TF-IDF evaluation: 5-fold cross-validation
* Tests passing: 12/12
* Final trained model: not completed yet

## Challenges / blockers

* The labeled data is still small
* Some MSML courses have very few reviews
* The current model is still a baseline, not the final model

## Next week's goal

* Add setup instructions so teammates can run the demo
* Prepare the final demo and report

## Individual contributions

* Moataz Abdelaziz (Product): Added Week 10 updates, low-evidence warning, tests, documentation updates, and Streamlit demo. (evidence: issue #42, PR #43)
* Abhiram Metuku (Data&Eval):  (evidence: issue #, PR #)
* Sriram Vema (Engineering):  Retrained on updated dataset, finalized model as distilBERT due to better performance (evidence: PR #45)

## Lean canvas changes

* The MVP should show when review evidence is limited
* The final project should focus on the working baseline pipeline 
