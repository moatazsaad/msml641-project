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
  metric: Percent of students who say the workload risk explanation would help them plan their schedule
  value: Product data requirements and workload labels created
  previous: MVP scope and baseline risk logic created
---

## Shipped this week

* Defined what data TerpLoad needs for the MVP. (evidence: issue #X, PR #Y)
* Created a simple workload label schema for the first NLP model. (evidence: issue #X, PR #Y)

## User / validation learning

* Based on the interviews, the first model should focus on the clearest workload signals: projects, exams, homework and time commitment.
* We narrowed the first model to four labels so it is easier to build and evaluate.

## Metrics snapshot

* Product data requirements document: created
* Workload labels defined: 4
* Schema file created: yes

## Challenges / blockers

* We still need real course review text.
* We need manually labeled examples before training the model.

## Next week's goal

* Collect course reviews text and label examples using the four workload labels.

## Individual contributions

* Moataz Saadeldin (Product): Defined product data requirements and created the workload label schema. (evidence: issue #8, PR #Y)
* Abhiram Metuku (Data&Eval): To be updated after teammate input. (evidence: ...)
* Sriram Vema (Engineering): To be updated after teammate input. (evidence: ...)

## Lean canvas changes (if any)

* The first model scope was narrowed to four workload labels: project-heavy, exam-heavy, homework-heavy, and time-consuming.