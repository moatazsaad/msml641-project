---

team: TerpLoad
week: 07
date: 2026-07-15
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
  metric: Midterm presentation readiness
  value: Midterm checkpoint prepared as a team
  previous: MVP labels and baseline logic aligned

---

## Shipped this week

* Prepared the midterm presentation structure. 
* Added simple tests for the baseline risk rules in `src/test_risk_rules.py`. 
* Started auditing the pilot labeled reviews. 
* Continued work on the TF-IDF pipeline and DistilBERT skeleton. 

## User / validation learning

The presentation focuses on the main user problem: students struggle to judge whether a planned course combination will be manageable before registration.

The current TerpLoad flow is:

* PlanetTerp reviews
* four workload labels
* baseline risk rules
* student-facing schedule risk report

## Metrics snapshot

* Workload labels: 4
* Risk-rule tests added: 5
* Midterm presentation structure: prepared
* Pilot label audit: in progress
* Trained classifier: not completed yet

## Challenges / blockers

* The pilot labels still need audit.
* The TF-IDF model is not fully connected yet.
* The full end-to-end flow is not complete yet.

## Next week's goal

* Finish label audit.
* Run the first TF-IDF baseline.
* Connect predicted labels to the risk report.

## Individual contributions

* Moataz Abdelaziz (Product): Prepared the midterm presentation structure and added simple tests for `src/risk_rules.py`. (evidence: issue #21, PR #Y)
* Abhiram Metuku (Data&Eval): Working on pilot label audit and labeling notes. (evidence: issue #21, PR #Y)
* Sriram Vema (Engineering): Working on TF-IDF pipeline and DistilBERT skeleton. (evidence: issue #21, PR #Y)

## Lean canvas changes

* The main focus is preparing for the midterm checkpoint and keeping the MVP scope realistic.
