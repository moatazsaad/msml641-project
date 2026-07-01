---
team: TerpLoad
week: 05
date: 2026-07-01
members:
  - name: Moataz Abdelaziz
    github: "@moatazsaad"
    hat: Product
  - name: Abhiram Metuku
    github: "@abhimet"
    hat: "Data&Eval"
  - name: Sriram Vema
    github: "@sriramvema"
    hat: Engineering
north_star:
  metric: rate of applying schema for reviews
  value: 10/10 labeled excerpts could be mapped to  current workload schema 
  previous: 
---

## Shipped this week

* Defined what data TerpLoad needs for the MVP. (evidence: issue #8, PR #9)
* Created a simple workload label schema for the first NLP model. (evidence: issue #8, PR #9)
* Made initial labeled review sample using excerpts from real course reviews. (evidence: PR #10)

## User / validation learning

We focused on whether our label schema works on real review text. We applied the four workload labels to real excerpts from CMSC330, CMSC351, and STAT400(Main courses mentioned in interviews)
We narrowed the first model to four labels so it is easier to build and evaluate:
* project_heavy
* exam_heavy
* homework_heavy
* time_consuming

## Metrics snapshot

* Product data requirements document: created
* Workload labels defined: 4
* Manually labeled review excerpts: 10
* Schema applicability rate: 10/10 excerpts
* Sample risk report: created
  
## Challenges / blockers

* We still need real course review text(actual full reviews) and current set is too small and manual but just an initial one to get an idea.
* some reviews mix several signal that imply self learning or harsh grading, so need to consider labelling style for those.
* need larger dataset for training
* see if we want to add the signals in addtl notes or add them as modifiers for the labels ( like risk modifiers)


## Next week's goal

* Start collecting and cleaning planetterp reviews (code for it)
* risk modifiers addition

## Individual contributions

* Moataz Abdelaziz (Product): Defined product data requirements and created the workload label schema. (evidence: issue #8, PR #9)
* Abhiram Metuku (Data&Eval): Created an initial manually labeled review sample using the four workload labels and added notes and confidence column to test whether the schema works on real review excerpts. (evidence: PR #10)
* Sriram Vema (Engineering): Created a text-based sample risk report showing how workload labels can help get an idea for students of what their combined schedule is. (evidence: PR #11)

## Lean canvas changes

* The first model scope was narrowed to four workload labels: project-heavy, exam-heavy, homework-heavy, and time-consuming.
* identified possible future risk modifiers, including self-learning, harsh grading, professor dependence, and course disorganization.
