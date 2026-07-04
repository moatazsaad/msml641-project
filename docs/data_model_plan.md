# Data Model Plan

## Data plan

The main data should come from course-related text, such as student course reviews, professor reviews, and course descriptions.

The first data source to test is PlanetTerp because it has UMD course and professor review text.

## NLP task

The first NLP task is multi-label classification.

The model will read a course review and predict whether the review shows specific workload signals.

Example review:

```text
The projects took forever and the exams were hard.
```

Expected labels:

```text
project_heavy = 1
exam_heavy = 1
homework_heavy = 0
time_consuming = 1
```

## First-version workload labels

The first model will use four workload labels:

* project_heavy
* exam_heavy
* homework_heavy
* time_consuming

## Future possible modifiers

These are useful ideas, but they are not first-version model labels yet:

* professor dependence
* harsh grading
* self-learning
* lab-heavy workload
* writing-heavy workload
* course disorganization

## Model plan

1. Start with a rule-based baseline.
2. Build a TF-IDF + Logistic Regression classifier.
3. If time allows, improve using sentence embeddings or DistilBERT.
4. Evaluate on held-out labeled reviews.

## Evaluation

* Split labeled reviews into train/test.
* Measure accuracy, precision, recall, and F1.
* Do error analysis on wrong predictions.

## Schedule risk

After predicting workload labels for each course, combine the course-level signals to estimate full-semester workload risk.
