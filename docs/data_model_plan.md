Data plan:
The main data should come from course related text, such as student course reviews, professor reviews and course descriptions.

NLP task:
Extract workload signals from text.

Example review:
"The projects took forever and the exams were hard."

Expected labels:
- project_heavy = 1
- exam_heavy = 1
- time_consuming = 1

Possible workload labels:
- project_heavy
- exam_heavy
- homework_heavy
- lab_heavy
- writing_heavy
- time_consuming
- professor_dependent
- uncertain_or_outdated

Model plan:
1. Start with a rule-based baseline.
2. Build a TF-IDF + Logistic Regression classifier.
3. If time allows, improve using sentence embeddings or DistilBERT.
4. Evaluate on held-out labeled reviews.

Evaluation:
- split labeled reviews into train/test
- measure accuracy, precision, recall, and F1
- error analysis on wrong predictions

Schedule risk:
After predicting workload signals for each course, combine the courses to estimate full-semester workload risk.