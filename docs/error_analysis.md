## Reviewed Mistakes

| # | Course | Model | Predicted issue | Note|
|---|---|---|---|---|
| 1 | CMSC216 | Keyword | Predicted project_heavy, exam_heavy, and homework_heavy even though the true label was mainly time_consuming. | The review mentions exams, homework, projects, and resources, but the actual workload signal is that students must stay on top of work constantly. This shows keyword matching can over-label when many course components are mentioned. |
| 2 | CMSC216 | Keyword | Predicted project_heavy and exam_heavy for a review mostly about academic-integrity stress and unclear process. | This is more of a professor/context issue than a core workload issue. It should be captured with modifiers like harsh_grading or disorganized_course, not automatically treated as project/exam workload. |
| 3 | CMSC250 | Keyword | Predicted exam_heavy for a positive Fawzi review saying quizzes/tests were not very difficult. | The word “exam” appears, but the review says the exams were manageable. This is a keyword false positive and shows why wording context matters. |
| 4 | CMSC216 | TF-IDF | Missed project_heavy when the review said projects were “hard but not unfair.” | This is a fair-but-heavy case. The course can still be project-heavy even if the review is positive and describes the work as fair. |
| 5 | CMSC216 | TF-IDF | Missed project_heavy for a review saying the class had 5 projects and the projects were difficult. | The model missed an important workload signal that directly affects the final schedule-risk report. This could understate project overlap risk. |
| 6 | CMSC250 | TF-IDF | Missed homework_heavy and time_consuming for a review saying quizzes/homework were difficult and more work than exams. | The model focused too much on exam language and missed that the main pressure came from homework/quizzes. This matters because homework-heavy courses can stack weekly. |
| 7 | STAT400 | DistilBERT | Predicted exam_heavy even though the review said the second midterm and final were fair/similar to practice. | DistilBERT may be over-predicting exam_heavy because the small dataset has many exam-heavy examples. This shows class imbalance can affect transformer predictions. |
| 8 | CMSC216 | DistilBERT | Missed project_heavy and time_consuming for a review saying projects were hard and students should not wait until the last day. | This is a major miss because project-heavy and time-consuming are exactly the signals TerpLoad needs for schedule planning. |
| 9 | CMSC351 | DistilBERT | Missed time_consuming for a review describing self-learning and major outside study effort. |  review implies time pressure through studying and possibly some self learning, model did not capture that though.  hows implied workload is harder than obvious keywords. |
| 10 | MSML604 | DistilBERT | Predicted exam_heavy for a review mostly saying averages were low but the professor curved generously. | Low averages or grade difficulty do not always mean exam-heavy workload. so need the grade/context information, not automatically as workload risk. |


Seemed like issue was with mixed reviews especially for keyword. Keyword is very sensitive to any mention of a label. TF-IDF also similar. DistilBERT was worse than both other models on our data (see `results/model_comparison.csv`) — this is an experiment we tried and are not using, not a candidate model. With only 64 labeled reviews, a transformer with millions of parameters does not have enough examples per label to fine-tune reliably, especially for `project_heavy` (11 positives) and `homework_heavy` (9 positives).

## Overfitting evidence

`predict_course_signals.py` trains on all 64 labeled reviews with no held-out portion,
then generates course signals. We checked what the model predicts on those same 64
reviews it was trained on: it matched the known label on **all 64 reviews, all 4 labels,
zero mismatches**. A model that perfectly reproduces 100% of its own training labels is
not demonstrating real skill — it is a sign of overfitting on a very small dataset. This is
further evidence that single-split accuracy numbers elsewhere in this project overstate how
well these models generalize to reviews they have not seen.

## More data did not clearly help (week10 update)

We labeled 40 more reviews (`data/weakly-labeled-week10.csv`, same weak-labeling method as
the original 64) and combined them with the original set, going from 64 to 104 labeled
reviews. `homework_heavy` went from 9 to 20 positive examples and `project_heavy` from 11
to 17. We expected this to improve TF-IDF's recall on those two labels.

It didn't, honestly: cross-validated macro F1 went from 0.3648 (64 reviews) to 0.3112 (104
reviews) - lower, not higher. `homework_heavy` recall is still exactly 0 even with 20
positive examples. `exam_heavy`'s F1 dropped noticeably (0.753 to 0.645) even though that
label already had plenty of data. Average accuracy ticked up slightly (0.7305 to 0.7404),
but that number is misleading here - on an imbalanced dataset, accuracy goes up just by
predicting "no" more often, which is the opposite of what this project needs.

Our best explanation: the new 40 reviews came from different courses/professors than a lot
of the original 64, so they add more varied vocabulary without necessarily adding more
*shared* wording for the model to learn from. A bag-of-words model like TF-IDF needs
positive examples that use similar language to generalize; 20 examples spread across
different ways of describing "homework was hard" may still not be enough. This suggests the
data bottleneck for `homework_heavy`/`project_heavy` is deeper than raw example count - it
may need 3-5x more labeled data than this, or a model less dependent on exact word overlap,
to move meaningfully. We are reporting this rather than hiding it.

## Reliability caveat

All accuracy/precision/recall/F1 numbers in `results/` are measured against **weak
labels** (see "What 'weak label' means" in `docs/labeling_guidelines.md`) — labels an LLM
assigned, not a human. Only 10 of the labeled reviews were ever spot-checked by a person
(the Week 7 audit), and 4 of those 10 were called "ambiguous." So these metrics show how
well each model matches the LLM's labels, not how well it matches true student-reported
workload. Treat every number here as a rough, small-sample estimate, not a validated
accuracy claim.
