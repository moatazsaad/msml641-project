## Reviewed Mistakes

| # | Course | Model | Predicted issue | Note|
|---|---|---|---|---|
| 1 | CMSC216 | Keyword | Predicted project_heavy, exam_heavy, and homework_heavy even though the true label was mainly time_consuming. | The review mentions exams, homework, projects, and resources, but the actual workload signal is that students must stay on top of work constantly. This shows keyword matching can over-label when many course components are mentioned. |
| 2 | CMSC216 | Keyword | Predicted project_heavy and exam_heavy for a review mostly about academic-integrity stress and unclear process. | This is more of a professor/context issue than a core workload issue. It should be captured with modifiers like harsh_grading or disorganized_course, not automatically treated as project/exam workload. |
