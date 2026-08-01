

i dont want split screen here:





what happend here now , is i pushed my local to my branch on github?


whats the assign on the right here?


Mon, Jun 22 at 8:57 PM

where to type here:



Pasted text(874).txt
Document
is it here:?



now 

i assigned myself and then went to this page ,and cant know how to go back to make them as reviwers

just for your info my temate made this last week:




expalin to me is the greeen the old or neww?


Pasted text(884).txt
Document







Pasted text(894).txt
Document

its hte mid term one:




TerpLoad_midterm_presentation(2).pptx
Presentation
here is the presentation,dont add slides ,just tell me where and what to add

now lets return to this:



read this and tell me is my reply good english:

Tue, Jul 14 at 5:32 PM
so now i openend a pull request,which means the main on github gets whats on my branch right?

Sun, Jul 19 at 6:53 PM
can i tyoe here or i can only choose?

also my teamate sent this for us to prpare  for wednesday, check my part and tell me what is it

is this what we were going to make?

why i cant see my branch oj github?


i have a question,why in the issue we didnt add only the important things he asked me to do?






8750e8b5-3959-4369-a127-41bf2136f02d.png
cd7c9692-c7f3-424a-a347-5453845b38d5.png








2002adfc-d3e0-4fda-9a8d-4348ce4f04b6.png
how to tell claude to do everyting without asking me?

Yes. Forget Claude for a second. To understand your project, follow this order.

Step 1 — Understand the project goal
Say this to yourself first:

TerpLoad helps a student enter planned courses and see if the schedule may be Low, Medium, or High workload risk.
The final flow is:

course reviews → workload labels → model predictions → course signals → risk rules → student report
Step 2 — Start from the final output
Open this file first:

data/course_workload_signals.json
This is the file the report uses.

It tells you things like:

CMSC216:
exam_heavy = true
time_consuming = true
review_count = 50
Meaning:

The model/report thinks CMSC216 has exam-heavy and time-consuming signals based on review data.
This file is important because it connects the model to the report.

Step 3 — Open the CLI report file
Open:

src/simple_report_cli.py
This is what the student uses in terminal.

It does this:

student enters courses
→ reads data/course_workload_signals.json
→ sends course signals to risk_rules.py
→ prints risk level, score, and reasons
Run it:

python src\simple_report_cli.py
Try:

CMSC216, CMSC330, CMSC351
Then try:

CMSC216, MATH410
The second test should show that MATH410 has no review data yet.

Step 4 — Open the risk logic
Open:

src/risk_rules.py
This file is not a machine learning model.

It is simple rules/math.

It takes labels like:

exam_heavy = true
time_consuming = true
and returns:

Low / Medium / High risk
risk score
reasons
This is the final risk calculator.

Step 5 — Understand where course_workload_signals.json comes from
Open:

src/predict_course_signals.py
This is the bridge file.

It does:

weakly labeled reviews
→ train TF-IDF + Logistic Regression
→ predict labels on cleaned reviews
→ average predictions per course
→ create data/course_workload_signals.json
Run it:

python src\predict_course_signals.py
After you run it, it updates:

data/course_workload_signals.json
So this file is how model predictions become course-level signals.

Step 6 — Understand the training data
Open these:

data/weakly-labeled-week08.csv
data/weakly-labeled-week10.csv
These are the labeled reviews.

Each row is a review with labels like:

project_heavy
exam_heavy
homework_heavy
time_consuming
Important:

These are weak labels, meaning AI-assisted labels reviewed/used for the project, not perfect human-certified labels.
So the model can be trained, but you should not claim it is perfect.

Step 7 — Understand the raw review data
Open:

data/cleaned_reviews.csv
This is the cleaned pool of PlanetTerp reviews.

The model uses this file to predict labels for reviews that are not labeled yet.

The rough idea:

104 labeled reviews teach the model
255 cleaned reviews are used to create course signals
Step 8 — Understand the model evaluation
Open:

src/train_tfidf_classifier.py
This file is for checking model performance.

It trains and evaluates TF-IDF + Logistic Regression.

It should write results like:

results/tfidf_metrics.json
results/tfidf_predictions.csv
Simple meaning:

This tells us how the baseline model is doing.
But remember:

The metrics are measured against weak labels, so they are useful but not final proof.
Step 9 — Understand why DistilBERT is not main
Open:

src/train_distilbert.py
Only read it. Do not focus too much on it.

Simple explanation:

DistilBERT is a stronger model, but our labeled dataset is too small for it right now.
TF-IDF is better as the main baseline.
Step 10 — Run the tests
Run:

python src\test_risk_rules.py
python src\test_simple_report_cli.py
Expected:

5 passed, 0 failed
5 passed, 0 failed
This means:

risk rules still work
CLI helper functions still work
Step 11 — Understand the whole project in one sentence
Memorize this:

TerpLoad collects course reviews, labels some reviews with workload signals, trains a TF-IDF baseline, creates course-level workload signals, and uses risk rules to show students a Low, Medium, or High schedule-risk report.
Best professional explanation
Because our labeled dataset is still small, we are not claiming a final high-accuracy model. Our focus is to build an honest end-to-end NLP pipeline that works, shows limitations clearly, and warns users when review evidence is limited.
Start by reading these three files in this order:

1. data/course_workload_signals.json
2. src/simple_report_cli.py
3. src/predict_course_signals.py
That will make the project click.


read this report and make it as the usual style of our reports and add my friends to it, also dont over engineer it and remove un needed things from it:
---

team: TerpLoad
week: 10
date: 2026-07-31

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
  metric: Honest, leakage-free evaluation pipeline
  value: Fixed the training/evaluation bugs, retired the models/claims that didn't hold up, and tested whether more labeled data actually helps
  previous: TF-IDF course signals connected to the CLI report, with initial model comparison and error analysis

---

## Shipped this week

* Fixed a data-leakage bug in src/predict_course_signals.py - it was letting the model "predict" on the exact reviews it was trained on. Now the real label is used for those reviews instead of asking the model to guess again.
* Fixed a mismatch between the evaluation script and the real deployed model - train_tfidf_classifier.py now uses the same class_weight="balanced" setting as production, so reported metrics describe the model actually being used.
* Replaced a single, noisy 80/20 train/test split with 5-fold cross-validation, so metrics are based on all labeled reviews instead of a lucky or unlucky 13-review sample.
* Added a low_evidence flag for any course with fewer than 10 reviews (e.g. MSML604 with 3, MSML605 with 2), and surfaced it as a plain warning in the CLI report instead of presenting thin data as fact.
* Retired DistilBERT from "candidate model" status. It scored worse than the keyword baseline (accuracy 0.15 vs 0.69); docs and results/model_comparison.csv now mark it clearly as a rejected experiment, not something the product uses.
* Documented what "weak label" means (labels an LLM assigned, not a human) directly in docs/labeling_guidelines.md, and added a reliability caveat to docs/error_analysis.md so every metric in results/ is clearly tied to that caveat.
* Labeled 40 more real, previously-uncollected reviews (data/weakly-labeled-week10.csv), combined with the original 64 for training (104 total), and measured the effect honestly - see Metrics snapshot below.
* Added 2 new tests covering the low-evidence warning logic (12/12 tests passing, up from 10/10).
* Built a Streamlit demo (app.py) that reuses the exact same risk-calculation functions as the CLI, so the web version and CLI can never disagree.

## User / validation learning

The main lesson this week wasn't from new user interviews - it was from testing our own assumption. We hypothesized that labeling 40 more reviews would improve the two weakest labels (project_heavy, homework_heavy). It didn't: cross-validated macro F1 went from 0.3648 to 0.3112, and homework_heavy recall stayed at exactly 0 even with 20 positive examples instead of 9. This tells us the gap is not "a few more labels" - it's a deeper data-volume problem than we expected, and it should shape how we scope the rest of the semester rather than assuming more labeling alone will fix it.

## Metrics snapshot

* Labeled reviews: 64 -> 104 (40 added this week, same weak-labeling method)
* project_heavy positive examples: 11 -> 17
* homework_heavy positive examples: 9 -> 20
* TF-IDF macro F1 (cross-validated): 0.3648 (64 reviews) -> 0.3112 (104 reviews) - more data did not clearly help
* homework_heavy recall: 0 before and after adding data
* Data-leakage bug in production course-signal generation: fixed
* Tests passing: 12/12 (was 10/10)
* DistilBERT status: confirmed rejected, not used in production
* Streamlit demo: built and smoke-tested (HTTP 200, no errors)

## Challenges / blockers

* More labeled data did not improve the TF-IDF model this week - homework_heavy is still undetectable even with 20 positive examples, suggesting the ceiling is deeper than raw example count.
* MSML604 (3 reviews) and MSML605 (2 reviews) still have very little evidence; MSML606 still has none.
* streamlit was added to the local virtual environment but there is no requirements.txt yet, so teammates can't install it the same way until that's added.
* Today's changes touch files across all three hats (labeling data, TF-IDF training, CLI/report code) and have not yet been reviewed by the team or opened as a PR.

## Next week's goal

* Decide as a team whether to invest further in labeling, given this week's finding that +40 reviews didn't move the metrics, or focus remaining effort on honestly reporting the data ceiling in the final write-up.
* Add a requirements.txt so the Streamlit demo is easy for teammates to run.
* Review this week's changes as a team before merging into the shared branch.
* Prepare the final report/demo framing around what the pipeline honestly can and can't do yet.

## Individual contributions

* Moataz Abdelaziz (Product): Fixed the data-leakage and evaluation-mismatch bugs, added cross-validation and the low-evidence warning, retired DistilBERT from production claims, labeled 40 more reviews and honestly evaluated their effect, added tests, and built the Streamlit demo. (evidence: this branch - not yet opened as a PR)

## Lean canvas changes

* The product now treats "how much evidence backs this" as part of the report itself (the low-evidence warning), not just an internal caveat - this is a shift toward honesty being a product feature, not just a disclaimer.
* We're moving away from assuming more labeled data is an easy fix; the plan for finishing the semester now needs to account for a real, measured data ceiling instead of an assumed one.

Use this cleaner Week 10 report:

---

team: TerpLoad
week: 10
date: 2026-07-31

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
  metric: Honest baseline evaluation
  value: TF-IDF pipeline checked, limitations documented, and low-evidence warnings added
  previous: TF-IDF course signals connected to the CLI report

---

## Shipped this week

* Fixed the course-signal pipeline so labeled reviews use their existing labels instead of being re-predicted by the model.
* Updated the TF-IDF evaluation to use 5-fold cross-validation.
* Added a low-evidence warning for courses with very few reviews.
* Added 40 more weak-labeled reviews, increasing the labeled set from 64 to 104.
* Updated the docs to explain weak labels and model limitations more clearly.
* Marked DistilBERT as not used because it did not perform well with the current small dataset.
* Added tests for the low-evidence warning.
* Built a simple Streamlit demo using the same report logic as the CLI.

## User / validation learning

The main learning this week is that more labels alone did not fix the weakest labels.

After adding 40 more weak-labeled reviews, the TF-IDF baseline still struggled with some labels, especially `homework_heavy`. This means the project should be honest about the current data limits instead of claiming the model is final.

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
* Some labels still have too few strong positive examples.
* MSML604 and MSML605 have very few reviews.
* MSML606 still has no review evidence.
* The model is a baseline, not a final production model.

## Next week's goal

* Review the Week 10 changes as a team.
* Decide whether to label more reviews or focus on final write-up and demo.
* Add setup instructions so teammates can run the demo easily.
* Prepare the final project framing around what the pipeline can and cannot do yet.

## Individual contributions

* Moataz Abdelaziz (Product): Fixed the course-signal pipeline, added low-evidence warnings, added tests, updated the report/demo flow, and documented model limitations. (evidence: issue #X, PR #Y)
* Abhiram Metuku (Data&Eval): Continued supporting the labeling and evaluation direction, including the weak-labeling workflow and dataset review. (evidence: issue #X, PR #Y)
* Sriram Vema (Engineering): Continued supporting the baseline/modeling pipeline and technical review of the model-to-report flow. (evidence: issue #X, PR #Y)

## Lean canvas changes

* The MVP should show when review evidence is limited.
* The final project should focus on an honest baseline pipeline instead of claiming a perfect model.
Replace issue #X and PR #Y after you create the issue and PR.


makde data 5 aug, delete the honest and those kind of words,sounds like ai writing it

Use this cleaner version:

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
* Built a simple Streamlit demo using the same report logic as the CLI.

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
* Abhiram Metuku (Data&Eval): Continued supporting the labeling and evaluation direction, including the weak-labeling workflow and dataset review. (evidence: issue #X, PR #Y)
* Sriram Vema (Engineering): Continued supporting the baseline/modeling pipeline and technical review of the model-to-report flow. (evidence: issue #X, PR #Y)

## Lean canvas changes

* The final project should focus on the working baseline pipeline and clearly explain its current limits


