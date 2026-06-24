---
team: "TerpLoad"
week: 04
date: "2026-06-24"
members:
  - name: "Abhiram Metuku"
    github: "@abhimet"
    hat: "Data&Eval"
  - name: "Sriram Vema"
    github: "@sriramvema"
    hat: "Engineering"
  - name: "Moataz Saadeldin"
    github: "@moatazsaad"
    hat: "Product"
north_star:
  metric: "Percent of students who say the workload risk explanation would help them plan their schedule"
  value: "4 interviews analyzed; 4/4 showed course-combination workload risk as a repeated pain point"
  previous: "Initial project direction selected"
---

## Shipped this week

Selected TerpLoad as the final project direction and narrowed it into a clear MVP scope before building further. Evidence: reports/week04.md.

Converted interview findings into clearer product direction, including proper user research summary, MVP requirements, and an NLP data and modelling plan. Evidence: #4, PR #5.

Created initial artifacts for workload labeling and course selection so future review collection can be evaluated consistently. Evidence: PR #6.



## Project Plan and Scope

Narrowed down project to TerpLoad idea and narrowed the MVP scope as well

Problem: UMD CS/STEM students often cannot tell whether a planned semester will become unmanageable because workload risk comes from how multiple courses stack through projects, exams, homework, and even unclear course structure.

Solution: TerpLoad lets a student enter a planned course schedule and returns a workload-risk breakdown with course-level signals, evidence from reviews, and confidence/uncertainty notes.

Why us: We plan to ground the product in UMD student interviews and course-review data, then turning unstructured reviews into evaluatable workload labels instead of giving a generic schedule opinion. 

MVP scope: A user can enter a small UMD CS/STEM course schedule and get a workload-risk report showing which courses or combinations are likely to be project-heavy, exam-heavy, time-consuming, or uncertain. 


## User / validation learning

From the 4 student interviews, we learned that the main pain is usually not one hard class by itself, but the way multiple difficult courses stack together in the same semester.

Students currently rely on friends, PlanetTerp, Reddit, and professor information, but this information can be incomplete, outdated, or specific to one professor or semester.

The most important missing information is project workload, exam difficulty, weekly time commitment, and course structure changes.

## Metrics snapshot

- Interviews analyzed: 4
- Repeated course-combination pain pattern: 4/4 interviews
- Baseline risk logic: created initial rule-based version

## Challenges / blockers

We still need reliable course review text and enough labeled examples to train an NLP model.

Course workload can change by professor, semester, and course structure, so TerpLoad should include confidence or uncertainty instead of giving an unsupported answer.

We need to decide which UMD CS/STEM courses to collect data for first.

## Next week's goal

Collect initial course reviews for UMD CS/STEM courses based on interviews as students mentioned specific courses repeatedly

## Individual contributions

Abhiram Metuku (Data&Eval): Defined the initial workload labeling guidelines for TerpLoad and began turning the project into NLP task by identifying workload labels. Evidence: PR #6.

Sriram Vema (Engineering): Combined Abhiram and Moataz's definitions into a detailed project flow, with steps describing data sources, example workflow indicators, proposed machine learning extension. Evidence docs/project_flow.md

Moataz Saadeldin (Product): Summarized interview findings, defined MVP requirements, wrote the NLP data/model plan, and added the baseline schedule risk scoring script. Evidence: #4, PR #5.

## Lean canvas changes

 main focus for project is on workload risk awareness for UMD CS/STEM students, not general course recommendation tool.

The value proposition shifted toward explaining why a schedule is risky using specific workload factors that could be from exams, homeworks, or professor style.

The main product risk is incomplete or outdated workload data because course structure can change by professor and semester but we plan to address by having flags saying that data might not be up to date...      
