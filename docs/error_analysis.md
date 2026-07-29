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


Seemed like issue was with mixed reviews especially for keyword. Keyword is very sensitive to any mention of a label. TF-IDF also similar. DistilBERT was definitely better but  needs a bigger sample and plan to use model predictions together with confidence levels, evidence snippets, and descriptive modifiers.
