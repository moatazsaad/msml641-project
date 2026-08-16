# TerpLoad — Final Submission

TerpLoad helps UMD CS/STEM students judge whether a planned semester schedule is
manageable before committing to it, by combining real PlanetTerp course reviews with a
fine-tuned DistilBERT model that flags workload signals (project-heavy, exam-heavy,
homework-heavy, time-consuming) per course, then rolling those into one schedule-level
risk rating.

**Live URL:** Not deployed. The app currently runs locally only — see setup below.

## What's in this folder

- `report.md` — the written final report (five required areas).
- `slides.md` — presentation slides.
- `report.md` and `slides.md` reference files throughout the main repository
  (`src/`, `data/`, `results/`) rather than duplicating content.

## Setup instructions

```
pip install -r requirements.txt
streamlit run app.py
```

The app uses the saved, fine-tuned DistilBERT model for all workload signals. Before
running it, `results/distilbert_model/` must exist and contain the Hugging Face model
files plus `thresholds.joblib` (both produced by `src/train_distilbert.py`). The app
never retrains on a student request.

For a course without an existing profile, TerpLoad fetches reviews from PlanetTerp,
classifies them with the saved model, and caches the result to
`data/cache/course_profiles_distilbert.json`. Later requests for that course reuse the
cached profile.

A command-line prototype is also available:

```
python src/simple_report_cli.py
```

It uses a separate, earlier TF-IDF-based signal file (`data/course_workload_signals.json`)
rather than live DistilBERT inference — see `report.md`, Area 2, for how the two differ.
