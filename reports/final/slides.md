<!--
TerpLoad — Final Presentation Slides
Each "---" starts a new slide. ~10-12 slides for a 10-12 minute talk.
-->

# TerpLoad
### Know your semester's workload before you commit

Moataz Abdelaziz · Abhiram Metuku · Sriram Vema
DATA/MSAI/MSML 641 — Natural Language Processing

---

## The problem

- Students don't struggle because of *one* hard class — it's the **combination**.
- Projects, exams, and homework from multiple courses stack badly in the same week.
- Nobody can see that stacking before the semester starts.

---

## Who it's for

UMD CS/STEM students planning a required or workload-heavy course combination —
especially students moving into harder major courses, or students who don't have a
choice in what they take together.

**What they do today:** ask friends who already took the course, check PlanetTerp,
Reddit, old GroupMes, or their advisor.

**The gap:** a friend's experience may not transfer — different professor, different
semester, different personal strengths. None of these sources combine multiple
students' experiences into one picture of a specific *combination* of courses.

---

## User research (4 interviews)

- Applied ML student: MSML604 + MSML605 + MSML606 together
- CS student: project-heavy CS courses + exam/essay-heavy GenEds
- CS+Econ student: CMSC216 + CMSC250 + organic chemistry + biology
- CS student: CMSC330 + CMSC351 + STAT400

All four said the semester was harder than expected. All four said they couldn't have
predicted it going in.

---

## What we built

Enter 3–5 planned course codes → get a **Low / Medium / High** risk rating, the
reasons behind it, per-course workload tags, and real review excerpts as evidence.

Two interfaces, one shared risk-scoring function (`risk_rules.py`):
- **Streamlit web app** — the current product
- **CLI prototype** — earlier, kept as the original testable version

---

## How it works end to end

```
Student enters courses
        |
        v
Course profile already cached? -- yes --> skip ahead to risk scoring
        |
        no
        v
Fetch reviews from PlanetTerp API
        |
        v
Classify each review with the saved, fine-tuned DistilBERT model
        |
        v
Aggregate into a workload profile (per-label rate + low-evidence flag)
        |
        v
estimate_schedule_risk() combines all courses
        |
        v
Report: risk level, confidence, reasons, evidence quotes
```

New courses are fetched and classified once, then cached. The app never retrains on a
student request.

---

## NLP task and data

- **Task:** multi-label classification — `project_heavy`, `exam_heavy`,
  `homework_heavy`, `time_consuming` per review.
- **Data:** PlanetTerp reviews → cleaned/deduplicated → weakly labeled by an LLM →
  Week 11 audit corrected 493 confirmed-wrong labels.
- **Final corpus:** 5,059 reviews, split 70/15/15 → train 3,541 / val 758 / test 760
  (fixed seed, held-out test touched only once).

---

## Models and baseline

- **Baseline:** keyword matching — no learned weights, no context.
- **TF-IDF + Logistic Regression** — 5-fold CV on train, threshold picked on val.
- **DistilBERT** — fine-tuned per label, same evaluation protocol.

| Model | Subset accuracy | Macro F1 | Micro F1 |
|---|---|---|---|
| TF-IDF | 0.537 | 0.652 | 0.667 |
| **DistilBERT (final)** | **0.647** | **0.739** | **0.738** |

DistilBERT wins on every metric — it's the model running in production.

---

## Where it fails

- Precision < recall on every label for both models — the system leans toward
  **over-flagging** a workload signal rather than missing it (the safer failure mode).
- Struggles with "fair but heavy" reviews (e.g. "hard but fair projects").
- Misses implied workload not stated in keywords (e.g. heavy self-learning).
- DistilBERT truncates long reviews at 256 tokens — late-review signals can be missed.
- Courses under 10 reviews get a low-evidence warning, not a confident flag.

---

## What users told us — and what we changed

- 10 students said the early CLI report was descriptive enough to influence a real
  decision.
- 14 testers on the Streamlit report: **14/14** found it helpful and easy to navigate,
  **64%** wanted more professor-specific signals, **21%** asked about courses with no
  reviews.
- → Shipped: **low-evidence warning** for thin-data courses.
- → Started, not yet wired into the app: a **grade-distribution fallback**
  (built and unit-tested, integration still pending).

---

## Ethics and limitations

- **Data rights:** public PlanetTerp API only, rate-limited, cached — no scraping.
- **Privacy:** no login, no accounts, nothing stored about the student using the tool.
- **Bias:** reviews are self-selected (strong opinions over-represented); labels are
  LLM-assigned weak labels, corrected in one direction (false positives) so far.
- **When it's wrong:** the system is tuned to over-warn rather than under-warn, phrases
  reasons as "may have," flags thin evidence, and states it doesn't replace advising.

---

## Demo

[Live or recorded demo]

---

## Questions?

Thank you.
