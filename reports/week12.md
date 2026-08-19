---

team: TerpLoad
week: 12
date: 2026-08-16

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
  metric: Final submission cleanup
  value: Final report draft, slide draft, and cleaned project files added
  previous: Corrected labels and model retraining

---

## Shipped this week

* Updated `docs/error_analysis.md` with the current DistilBERT result
* Deleted 4 dead files:
  * `data/clean_review.csv`
  * `data/llm_labeled_week06.json`
  * `data/labeled_reviews_sample.csv`
  * `data/results/label_distribution.csv`
* Added first draft of the final submission in `reports/final/`
* Added `reports/final/report.md`
* Added `reports/final/slides.md`
* Added `reports/final/README.md`

## User / validation learning

The main learning this week was that the final submission needed to match the current project state.

Some older docs still described outdated model results, so they were cleaned up before the final report and slides.

The current TerpLoad flow is:

* cleaned PlanetTerp reviews
* corrected workload labels
* TF-IDF and DistilBERT evaluation
* course workload signals
* risk rules
* Streamlit / CLI report
* final report and presentation materials

## Metrics snapshot

* Dead files removed: 4
* Final report draft added: yes
* Final slide draft added: yes
* Final README/setup notes added: yes
* Error analysis updated: yes
* Final submission draft location: `reports/final/`

## Individual contributions

* Moataz Abdelaziz (Product): Updated error analysis, cleaned dead files, drafted the final report, drafted the final slides, and added final setup notes. (evidence: issue #52, PR #53)
* Abhiram Metuku (Data&Eval):  (evidence: issue #X, PR #Y)
* Sriram Vema (Engineering): (evidence: issue #X, PR #Y)

