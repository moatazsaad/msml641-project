]---

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

## Metrics snapshot

- Raw PlanetTerp reviews collected: about 903
- Cleaned reviews available: 255
- Pilot LLM-labeled reviews: 30
- Week 8 weak-labeled reviews: 64
- Core workload labels: 4
- Descriptive modifiers: 4

## Challenges / blockers

* The pilot labels still need audit-- need more auditing.
* The TF-IDF model is not fully connected yet.
* The full end-to-end flow is not complete yet.

## Next week's goal

- The weak-labeled dataset is small and not fully human-verified.
- Some reviews focus on professor style or grading rather than direct workload.
- MSML606 had no cleaned reviews ava/ilable in the current dataset.
- project_heavy and homework_heavy have fewer positive examples than exam_heavy and time_consuming.
- Baseline results should be treated as early signals, not final model perfo


## Individual contributions

* Moataz Abdelaziz (Product): 
* Abhiram Metuku (Data&Eval):  Created the Week 8 review sample, weak-labeled dataset, label distribution, and labeling notes.  
  (evidence: issue #,26 PR #27
* Sriram Vema (Engineering):   (evidence: issue #, PR #)
  
## Lean canvas changes

- We are keeping the MVP focused on an evidence-backed schedule-risk report.
- The first model targets remain limited to four workload labels.
- Descriptive modifiers will support report explanations, but not drive first-model training.
- We will avoid overconfident recommendations and show limited-evidence warnings when review counts are low.
