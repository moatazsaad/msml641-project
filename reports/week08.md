---

team: TerpLoad
week: 07
date: 2026-07-22

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
  metric: Schedule report usefulness
  value: Weak-labeled data created and first baselines run
  previous: Midterm checkpoint prepared as a team

---

## Shipped this week
- Created a 64-review weak-labeled dataset for first baseline experiments.
- Added reviews to label with the selected review sample.
- Added a weakly labeled csv file with four core workload labels and descriptive modifiers.
- Added a label distribution file with positive counts for each label.
- Added labelling notes explaining the labeling process, audit connection, and limitations for this week.
- Ran a keyword baseline on the four core workload labels.
- Continued work on the TF-IDF pipeline and DistilBERT skeleton. 

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

* The pilot labels still need audit-- need more auditing.
* The TF-IDF model is not fully connected yet.
* The full end-to-end flow is not complete yet.

## Next week's goal

* Finish label audit.
* Run the first TF-IDF baseline.
* Connect predicted labels to the risk report.

## Individual contributions

* Moataz Abdelaziz (Product): 
* Abhiram Metuku (Data&Eval):  Created the Week 8 review sample, weak-labeled dataset, label distribution, and labeling notes.  
  (evidence: issue #,26 PR #27
* Sriram Vema (Engineering): 

## Lean canvas changes

- We are keeping the MVP focused on an evidence-backed schedule-risk report.
- The first model targets remain limited to four workload labels.
- Descriptive modifiers will support report explanations, but not drive first-model training.
- We will avoid overconfident recommendations and show limited-evidence warnings when review counts are low.
