# Labeling Workload Guidelines
working draft for the terpload labels. Main goal is to label course reviews for workload signals that constantly come up in interviews like projects, exams, time commitment, professor/course structure, and if workload stacks badly across classes

These labels are not final. We expect to update them after labeling the first batch of reviews.

## How to label

Each review can have more than one label.

Use `1` if the review clearly supports the label.  
Use `0` if the review does not support the label.

If the review is vague, leave a note instead of forcing the label.

## Workload labels

Workload labels describe what the review says about the course workload.

### project_heavy

review mentions large projects, frequent projects, coding projects, group projects, or projects taking a lot of time.

Examples:
-  projects took forever.”
- “Start the projects early.”
- “Most of the work came from programming assignments.”

### exam_heavy

Review describes exams, quizzes, midterms, or finals as difficult, frequent, heavily weighted, stressful, or central to passing.

Examples:
- “The exams were brutal.”
- “Three exams made up most of the grade.”
- “You need to study a lot for every quiz.”

### homework_heavy

Review describes homework, assignments, worksheets, labs, or problem sets as frequent, long, difficult, or a major weekly burden.

Examples:
- “There was homework every week.”
- “The assignments took hours.”
- “The labs added a lot of work.”

### time_consuming

Review says the course requires substantial time, repeated effort, long study hours, or is difficult to balance with other courses.

Examples:
- “This class took up most of my week.”
- “You need to start everything early.”
- “It was hard to balance with my other classes.”

## Experimental risk modifiers

These are being collected this week, but they are not first-version model labels yet.

### self_learning_required

Review says students must teach themselves or rely heavily on textbooks, recorded videos, outside resources, or independent study because lectures are insufficient.

Examples:
- “You basically have to teach yourself.”
- “I learned everything from the textbook.”
- “The lectures were useless, so I used YouTube.”

### harsh_grading

Review describes grading as strict, unforgiving, unfair, inconsistent, nitpicky, or giving little partial credit.

Examples:
- “The exams were graded extremely harshly.”
- “Small mistakes lost most of the points.”
- “There was almost no partial credit.”

### disorganized_course

Review describes unclear requirements, vague instructions, late grading, poor communication, inconsistent answers, or poorly structured materials.

Examples:
- “The project instructions were vague.”
- “Grades were returned weeks late.”
- “The TAs and professor gave conflicting answers.”

good = correctly labelled by LLM
ambiguous = labels not identified but review mentions useful info(hw graded strictly, even if heavy not mentioned)
corrected = wrongly identified

After audtiting, found that the risk modifieres can be added but not for first model but still add context. Can have them as keyword based and use those keywords to determine harshness/disorganization. 
