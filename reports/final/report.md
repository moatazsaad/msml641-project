# TerpLoad

## 1. Problem and users

UMD students can already find information about individual courses through sources such as PlanetTerp, Reddit, friends, GroupMe conversations, and academic advisors. The harder problem is determining how the workloads of several planned courses may stack together during one semester.

TerpLoad is designed primarily for UMD CS and STEM students planning workload-heavy course combinations. This includes students entering more demanding major courses, students balancing several required courses at once, and students who want a clearer picture of their semester before registration.

We interviewed four students who had experienced this problem across different CS, STEM, and graduate schedules. Their experiences suggested that understanding individual courses was not always enough to anticipate how the full semester workload would feel.

Before TerpLoad, students pieced this information together from friends who had already taken a course, PlanetTerp reviews, Reddit, past GroupMe conversations, and academic advisors. Friends were the most trusted source in our interviews, but experiences can differ by professor, semester, and student. TerpLoad addresses this gap by combining student-review evidence across multiple courses into one schedule-level workload view.

## 2. Product

TerpLoad takes 1–6 planned UMD course codes and returns a Low / Medium / High workload risk rating or an Uncertain result when review evidence is too limited. The report also shows the reasons behind the result and a per-course breakdown of which workload signals (project-heavy, exam-heavy, homework-heavy, time-consuming) appear in real student reviews. Additionally, real review excerpts are shown as evidence so the student is not just trusting a number.

The final product is a Streamlit web app (`app.py`). An earlier command-line prototype (`src/simple_report_cli.py`) is also kept in the repository. Both use the same `estimate_schedule_risk()` logic from `src/risk_rules.py`, although their results may differ if the underlying course signals come from different model outputs or data sources. The Streamlit app is the current production path and uses saved DistilBERT inference.

**How it works end to end (the live web app path):**

```
Student enters course codes (e.g. CMSC330, CMSC351, STAT400)
        |
        v
Course profile already cached? -- yes --> skip ahead to risk scoring
        |
        no
        v
Fetch reviews from PlanetTerp's public API (src/planetterp_client.py)
        |
        v
Classify each review with the saved, fine-tuned DistilBERT model
(src/distilbert_inference.py)
        |
        v
Aggregate into a course workload profile: per-label positive rate,
True/False flag, low-evidence warning if under 10 reviews
        |
        v
estimate_schedule_risk() combines all courses' profiles into one
risk score, level, and list of reasons
(src/risk_rules.py — same function used by the CLI)
        |
        v
Report shown to the student:
risk / uncertainty, confidence, main driver,
best-move advice, workload signals, and evidence
```

New courses are fetched and analyzed with the saved DistilBERT model, then their course
profiles are cached for reuse. The model is not retrained when a student submits a
schedule.

The confidence shown in the report represents the amount of review evidence available,
not DistilBERT model probability. Courses with very limited or missing review evidence
are handled with low-confidence or Uncertain states instead of receiving an overly
confident conclusion.

Historical grade distributions and recent professor context are also shown in the final
app as additional decision context. They remain separate from the NLP pipeline and do
not affect workload labels or schedule risk.


## 3. NLP method and evaluation

TerpLoad frames the NLP problem as multi-label classification of student course reviews. For each PlanetTerp review, the model predicts whether the text contains evidence of one or more of four workload categories:

- project_heavy
- exam_heavy
- homework_heavy
- time_consuming

The task is multi-label rather than single-label because the same review can describe several types of workload at once. For example, a student may describe a course as both exam-heavy and time-consuming.

### Data and Labeling
Reviews were collected from PlanetTerp, cleaned, and deduplicated before labeling. The project used weak labels created with an LLM following a written labeling prompt and labeling guidelines. Because weak labels can contain mistakes, we later performed a manual audit and corrected 493 confirmed incorrect label assignments.

The final dataset contains **5,059 reviews** and was split 70/15/15:

| Split | Reviews |
|---|---:|
| Train | 3,541 |
| Validation | 758 |
| Held-out test | 760 |

The held-out test set was reserved for the final model comparison.

### Model development

The NLP approach developed through three stages.

The first stage was a keyword/rule-based prototype (`src/workload_baseline_signal.py`). This initial approach detected explicit terms such as project, exam, or homework, but it was highly sensitive to wording and could fail when a term appeared in a reassuring context.

Next, we used **TF-IDF + Logistic Regression** as a statistical baseline. TF-IDF converts review text into weighted word and n-gram features, while Logistic Regression learns a classifier for each workload label. This was stronger than the keyword approach but still relied heavily on lexical overlap rather than contextual language understanding.

The final choice of model was a **fine-tuned DistilBERT multi-label classifier**. The review text is tokenized into subword tokens with a maximum sequence length of 256 and passed through DistilBERT to a four-output multi-label classification head. This model was then fine-tuned for three epochs with a batch size of 8. Finally, the saved model produces review-level scores, and label-specific decision thresholds convert those scores into positive or negative predictions for each workload category.

### Held-out evaluation

Both learned approaches were evaluated on the same 760-review held-out test set.

| Model | Subset Accuracy | Macro F1 | Micro F1 |
|---|---:|---:|---:|
| TF-IDF + Logistic Regression | 0.537 | 0.652 | 0.667 |
| Fine-tuned DistilBERT | **0.647** | **0.739** | **0.738** |

DistilBERT improved Macro F1 from **0.652** to **0.739** while also improving subset accuracy and Micro F1, so it was selected for the final Streamlit application.

The final DistilBERT per-label F1 scores were:

| Label | F1 |
|---|---:|
| `project_heavy` | 0.746 |
| `exam_heavy` | 0.734 |
| `homework_heavy` | 0.741 |
| `time_consuming` | 0.736 |

Macro F1 is especially useful for this project because it evaluates each of the four labels separately and gives them equal importance rather than allowing the most common label to dominate the overall score.

### From review predictions to course signals

DistilBERT makes predictions at the **individual-review level**, not directly at the course or schedule level. For each course, TerpLoad calculates the percentage of reviews predicted positive for each workload category. A category becomes an active course-level signal when at least **30% of the available reviews** are predicted positive for that category.

We used 30% as an aggregation threshold so that a workload category needs support from a meaningful portion of the available reviews before it affects the course profile. This is a downstream product rule rather than something learned by DistilBERT. Because the task is multi-label, multiple workload signals can be active for the same course.

### Error Analysis

The final DistilBERT model still makes mistakes, especially when a review contains ambiguous or mixed language. For example, we observed cases where discussion of low exam averages or difficult grading was classified as `exam_heavy` even when the review also explained that the professor curved generously. This shows that grade difficulty does not always mean the course has an exam-heavy workload.

Mixed reviews are another challenge because a single student may discuss exams, projects, homework, professor quality, and overall time commitment in the same review. DistilBERT handled this contextual language better than our earlier approaches, but the boundaries between the specific workload categories can still be unclear.

There is also a course-level limitation when review counts are small. For example, if a course has only three reviews and one is classified positively for a workload category, that produces a 33% positive rate and crosses our 30% course-level threshold. This is an aggregation issue rather than necessarily a model error. To reduce the chance of presenting sparse evidence too confidently, TerpLoad marks courses with fewer than 10 reviews as low evidence and can return an `Uncertain` schedule result when review coverage is insufficient.

Finally, our evaluation is measured against the corrected weak-label dataset rather than a fully human-annotated gold-standard dataset. Although we manually audited the data and corrected 493 confirmed incorrect label assignments, some labeling noise still may remain. Future work could use a larger independently human-annotated test set and evaluate course-level aggregation thresholds more systematically.


## 4. User evidence

We first interviewed four UMD students to understand how they currently evaluate course workload and where existing methods fall short. These interviews reinforced the main product problem: students could often learn about individual courses but struggled to understand how different workload types would combine across an entire semester.

Later, **14 users in total, including the initial interviewees, evaluated an earlier TerpLoad prototype and simple schedule report**. This testing occurred before the final Streamlit interface.

The prototype generated workload signals and schedule-level information that users could evaluate. All 14 participants indicated that the report was useful for understanding a planned schedule, while their questions also exposed information that was missing from the prototype.

Two findings directly influenced later development:

- **9 of 14 users wanted professor-specific information.** Because workload can vary by instructor, we added recent professor context to the final application. Professor ratings remain separate context and do not affect DistilBERT predictions or schedule risk. To keep this context current, the app only includes professors with recent PlanetTerp activity in the 2024–2026 window rather than displaying every historical instructor associated with the course.

- **3 of 14 users asked what would happen when a course had no reviews.** This led us to make missing and limited evidence explicit rather than silently producing a normal result. The final product includes `NO COURSE REVIEWS`, `LIMITED DATA`, lower confidence, and `UNCERTAIN` handling when appropriate.

We also added historical grade distributions as additional decision context while intentionally keeping them separate from the workload model. Grades and professor information help students investigate a course further but never change its workload labels or schedule-risk result.

The user study changed the final product beyond its original prototype. Rather than only returning a risk result, the final TerpLoad interface exposes the available evidence, communicates when that evidence is weak, and gives students additional context for investigating the courses in their schedule.

A limitation of this evidence is that the **14 participants evaluated the prototype/simple report rather than the final Streamlit interface**. Therefore, this study does not directly validate the usability of the final UI. In future work, we would conduct another study in which students complete course-planning tasks directly in the deployed application and measure whether the final interface improves or changes their scheduling decisions.

## 5. Ethics and limitations

TerpLoad is intended as a **decision-support tool**, not as a perfect predictor of whether a student should take a course or whether they will succeed in a particular schedule. The system aims to summarize patterns found in available student reviews, which naturally introduces several ethical and technical limitations.

### Data rights and privacy

TerpLoad uses course reviews and related course information available through PlanetTerp. The application does not ask users to provide personal academic records, grades, GPA, demographic information, or other sensitive student data. A user only enters the course codes they are considering.

Review text is used to identify workload patterns and provide supporting evidence. Because reviews were originally written by students for a public course-review platform rather than specifically for TerpLoad, we treat them as evidence about reported course experiences rather than objective descriptions of a course or its students.

### Bias and representation

Reviews on PlanetTerp are self-selected. Students who choose to leave reviews may have had particularly positive or negative experiences, while students with more typical experiences may never post. Review coverage also differs substantially across courses. TerpLoad cannot automatically assume that the available reviews represent every student who has taken a course.

Workload is also subjective. A course that one student considers extremely time-consuming may be manageable for another student depending on prior knowledge, outside responsibilities, learning style, and instructor. TerpLoad therefore reports patterns in review text rather than claiming to predict an individual student's experience.

Weak labeling introduces another source of potential bias and error. Although we manually audited the dataset and corrected **493 confirmed incorrect label assignments**, the final evaluation is still based on corrected weak labels rather than a completely independently human-annotated gold-standard dataset.

### When the model is wrong

False positives and false negatives have different consequences. A false positive may cause a course to appear more workload-heavy than the reviews actually support, potentially discouraging a student from taking a manageable schedule. A false negative may hide a real workload pressure and make a difficult schedule appear safer than it is.

TerpLoad reduces the impact of these errors by showing the evidence behind its conclusions rather than presenting only a risk score. Users can inspect review counts, workload percentages, and supporting excerpts. Courses with limited review evidence are identified as such, and insufficient evidence can produce an `UNCERTAIN` result rather than a confident workload judgment.

Professor ratings and historical grade distributions are provided only as additional context. They do not modify DistilBERT predictions or schedule risk, which prevents unrelated signals such as a low historical grade distribution from automatically being interpreted as evidence of heavy workload.

### Additional limitations

The final system still has several important limitations:

- The **30% course-level threshold is a product heuristic**, not a learned or statistically optimized threshold.
- Courses with very few reviews can produce unstable percentages; for example, one positive review out of three already represents 33%.
- Courses and instructors can change over time, so older reviews may not perfectly represent the current version of a course.
- DistilBERT uses a maximum input length of 256 tokens, meaning information near the end of very long reviews may be truncated.
- The held-out evaluation uses a review-level split, so the results measure performance on unseen reviews rather than guaranteeing generalization to completely unseen courses.
- Schedule risk is produced by transparent deterministic rules over course-level workload signals rather than a model trained on actual student schedule outcomes.
- The current user study evaluated the earlier prototype/simple report rather than the final Streamlit interface.

Future work could include a larger independently human-labeled evaluation set, more diverse training reviews, systematic testing of the 30% aggregation threshold, evaluation on unseen courses, and direct user testing of the deployed Streamlit application.

Another future direction would address courses with little or no review data. Rather than returning only an uncertain result, TerpLoad could analyze official course descriptions and compare them with patterns learned from better-documented courses with similar content or structure. This could provide a preliminary workload estimate when direct review evidence is unavailable, while clearly distinguishing that estimate from one supported by actual reviews of the course.

Additional student discussion sources could also provide useful evidence. We originally considered sources such as the UMD subreddit, but reliable access to that data was not available for the current project. If an appropriate and permitted data-access method becomes available, future versions could investigate whether those discussions add useful workload evidence beyond PlanetTerp reviews.


