# TerpLoad LLM Labeling Prompt

You are labeling course-review excerpts for the TerpLoad NLP project.

The source data comes from PlanetTerp reviews. These reviews often mix professor feedback, workload details, grading concerns, course structure, and unrelated opinions.

For each excerpt, assign binary labels using only the excerpt text.

## Labels

### relevant_to_workload_or_risk

Use `1` when the excerpt contains useful evidence about workload, assessment pressure, time demand, self-learning, grading strictness, or course organization.

Use `0` when it is only about professor personality, general praise or dislike, unrelated anecdotes, or information that does not support any workload or risk label.

### project_heavy

Use `1` when projects are described as long, difficult, frequent, stressful, heavily weighted, or requiring an early start.

### exam_heavy

Use `1` when exams, quizzes, midterms, or finals are described as difficult, frequent, stressful, heavily weighted, or central to success in the course.

### homework_heavy

Use `1` when homework, assignments, worksheets, labs, or problem sets are described as frequent, long, difficult, tedious, or a major weekly burden.

### time_consuming

Use `1` when the excerpt describes substantial time commitment, repeated effort, difficulty balancing the course, work taking multiple days, or the need to start early because of workload.

### self_learning_required

Use `1` when students are described as needing to teach themselves or rely heavily on textbooks, recorded videos, YouTube, outside resources, or independent study because lectures are insufficient.

### harsh_grading

Use `1` when grading is described as strict, unforgiving, unfair, inconsistent, nitpicky, or providing little partial credit.

### disorganized_course

Use `1` when the excerpt describes vague requirements, late grading, poor communication, inconsistent answers, changing expectations, or poorly structured course materials.

## Rules

- More than one label may be `1`.
- Use only the excerpt text.
- Do not infer from professor name, course code, rating, review year, or outside knowledge.
- Do not assign a label merely because a keyword appears.
- Positive statements matter too. For example, “the exams were easy” should not be labeled `exam_heavy`.
- When `relevant_to_workload_or_risk = 0`, all seven workload and modifier labels must be `0`.
- Use confidence values: `high`, `medium`, or `low`.
- Keep notes brief.
- Return valid JSON only.

## Required JSON format

```json
[
  {
    "excerpt_id": "CMSC216_001_E01",
    "relevant_to_workload_or_risk": 1,
    "project_heavy": 1,
    "exam_heavy": 0,
    "homework_heavy": 0,
    "time_consuming": 1,
    "self_learning_required": 0,
    "harsh_grading": 0,
    "disorganized_course": 0,
    "confidence": "high",
    "notes": "Projects are described as long and requiring an early start."
  }
]