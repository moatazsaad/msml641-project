## Reviewed Mistakes

| # | Course | Model | Predicted issue | Note|
|---|---|---|---|---|
| 1 | CMSC216 | Keyword | Predicted project_heavy, exam_heavy, and homework_heavy even though the true label was mainly time_consuming. | The review mentions exams, homework, projects, and resources, but the actual workload signal is that students must stay on top of work constantly. This shows keyword matching can over-label when many course components are mentioned. |
| 2 | CMSC216 | Keyword | Predicted project_heavy and exam_heavy for a review mostly about academic-integrity stress and unclear process. | This is more of a professor/context issue than a core workload issue. It should be captured with modifiers like harsh_grading or disorganized_course, not automatically treated as project/exam workload. |
| 3 | CMSC250 | Keyword | Predicted exam_heavy for a positive Fawzi review saying quizzes/tests were not very difficult. | The word “exam” appears, but the review says the exams were manageable. This is a keyword false positive and shows why wording context matters. |
| 4 | CMSC216 | TF-IDF | Missed project_heavy when the review said projects were “hard but not unfair.” | This is a fair-but-heavy case. The course can still be project-heavy even if the review is positive and describes the work as fair. |
