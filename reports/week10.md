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
  metric: Baseline evaluation and report reliability
  value: TF-IDF pipeline checked, low-evidence warnings added, and report flow updated
  previous: TF-IDF course signals connected to the CLI report

---

## Shipped this week

* Fixed the course-signal pipeline so labeled reviews use their existing labels instead of being re-predicted by the model.
* Updated the TF-IDF evaluation to use 5-fold cross-validation.
* Added a low-evidence warning for courses with very few reviews.
* Added 40 more weak-labeled reviews, increasing the labeled set from 64 to 104.
* Updated the docs to explain weak labels and model limitations more clearly.
* Marked DistilBERT as not used because it did not perform well with the current dataset.
* Added tests for the low-evidence warning.
* Built a Streamlit demo using the same report logic as the CLI - risk level, confidence, a best-move recommendation, workload tags, and real quoted evidence from the labeled reviews.
* Reran the full pipeline end to end to check everything still works together, cleaned up a couple leftover comments in the process.
* Merged in Abhiram's course list update (8 courses -> 32), verified the pipeline still works the same afterward.

## User / validation learning

The main learning this week is that adding more weak-labeled reviews did not fully solve the weaker label performance.

After adding 40 more reviews, the TF-IDF baseline still struggled with some labels, especially `homework_heavy`. This shows that the current dataset still needs more consistent labeled examples before the model can be treated as final.

The current TerpLoad flow is:

* cleaned PlanetTerp reviews
* weak workload labels
* TF-IDF baseline
* course workload signals
* low-evidence warning
* CLI / Streamlit report

## Metrics snapshot

* Labeled reviews: 104
* Reviews added this week: 40
* Workload labels: 4
* TF-IDF evaluation: 5-fold cross-validation
* Low-evidence warning: added
* Tests passing: 12/12
* DistilBERT status: not used
* Final trained model: not completed yet

## Challenges / blockers

* The labeled dataset is still small.
* Some labels still have too few positive examples.

## Next week's goal

* Add setup instructions so teammates can run the demo easily
* Prepare the final project framing around the current pipeline

## Individual contributions

* Moataz Abdelaziz (Product): Fixed the course-signal pipeline, added low-evidence warnings, added tests, updated the report/demo flow, and documented model limitations. (evidence: issue #X, PR #Y)
* Abhiram Metuku (Data&Eval): Expanded the course list from 8 to 32 courses, tagged each as interview-sourced or course-pool, to widen future review collection. (evidence: PR to be linked)
* Sriram Vema (Engineering): Continued supporting the baseline/modeling pipeline and technical review of the model-to-report flow. (evidence: issue #X, PR #Y)

## Lean canvas changes

* The final project should focus on the working baseline pipeline and clearly explain its current limits
