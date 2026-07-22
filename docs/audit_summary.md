# Week 7 Audit Summary 

## Notes
* Some of the reviews don't mention our main workload signals explicitly -- more focused on professor style
* labelled those as ambiguous- if it doesnt mention that, student still needs to understand workload level without being stressed.
* Some didn't have homework heavy labelled but mentioned the homeworks were graded STRICTLY so need to take into account
* from all of them -- have new idea of allowing students to pick the professor as they enter the course.
* need to put these to side and use as notes for updating labelling guidelines as we go.
  
## Audit Results

Audited reviews: 10

- good: 6
- corrected: 0
- ambiguous: 4

## Main Finding

Most audit issues were ambiguity issues rather than direct labeling errors. The LLM labels were usually reasonable, but several reviews contained professor-style information or positive-but-challenging signals that did not map cleanly to the four core workload labels.

This suggests that Week 08 weak labeling should use clearer rules for ambiguous cases rather than expanding the first model targets.

## Audit-Based Guideline Updates

Based on the audit, we added the following clarifications:

- Do not mark `project_heavy` only because a review mentions projects. The review should describe projects as long, frequent, intensive, difficult, or a major part of the workload.
- Do not mark `homework_heavy` only because homework is graded strictly. The review should mention homework frequency, length, difficulty, or time burden.
- Mark `exam_heavy` when exams are heavily weighted, unusually difficult, frequent, or central to the grade, even if the review is overall positive.
- Positive reviews can still contain workload signals. A course can be well-taught but still exam-heavy or project-heavy.
- Professor/course context such as strict grading, disorganization, or self-learning should be saved as descriptive modifiers, not first-model targets.
- Add a separate modifier for `fair_but_strict` when reviews describe grading or exams as strict/challenging but fair.
