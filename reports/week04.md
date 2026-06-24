---

team: TerpLoad
week: 04
date: 2026-06-24
members:

* name: Abhiram Metuku
  github: "@abhimet"
  hat: "Data&Eval"
* name: Sriram Vema
  github: "@sriramvema"
  hat: Engineering
* name: Moataz Saadeldin
  github: "@moatazsaad"
  hat: Product
  north_star:
  metric: Percent of students who say the workload risk explanation would help them plan their schedule
  value: 4 interviews analyzed; 4/4 showed course-combination workload risk as a repeated pain point
  previous: Initial project direction selected

---

## Project scoping

* Problem: UMD CS/STEM students planning difficult semesters struggle to know how multiple course workloads will stack together before registering.
* Solution: TerpLoad will analyze course-related text and workload signals to give students a schedule risk level with clear reasons.
* Why us: Our interviews showed the exact pain point, and our NLP approach focuses on UMD CS/STEM workload signals like projects, exams, time commitment, and professor/course-structure uncertainty.
* MVP scope: A user can enter a planned UMD CS/STEM course schedule and get a Low, Medium, or High workload risk result with the main reasons.

## Shipped this week

* Transformed interview findings into clearer product direction for TerpLoad, including a user research summary, MVP requirements, and an NLP data/model plan. (evidence: #4, PR #5)
* Added a simple baseline schedule risk scoring script in `src/risk_rules.py` to give the team a starting point before building the NLP model. (evidence: #4, PR #5)

## User / validation learning

* From the 4 student interviews, we learned that the main pain is usually not one hard class by itself, but the way multiple difficult courses stack together in the same semester.
* Students currently rely on friends, PlanetTerp, Reddit, and professor information, but this information can be incomplete, outdated, or specific to one professor or semester.
* The most important missing information is project workload, exam difficulty, weekly time commitment, and course structure changes.

## Metrics snapshot

* Interviews analyzed: 4
* Repeated course-combination pain pattern: 4/4 interviews (was unknown before interviews)
* Baseline risk logic: created initial rule-based version

## Challenges / blockers

* We still need reliable course review text and enough labeled examples to train an NLP model.
* Course workload can change by professor, semester, and course structure, so TerpLoad should include confidence or uncertainty instead of giving an unsupported answer.
* We need to decide which UMD CS/STEM courses to collect data for first.

## Next week's goal

* Collect initial course reviews for UMD CS/STEM courses based on interviews as students mentioned specific courses repeatedly

## Individual contributions

* Abhiram Metuku (Data&Eval): Defined the initial workload labeling guidelines for TerpLoad and began turning the project into NLP task by identifying workload labels. Evidence: PR #6.
* Sriram Vema (Engineering): Combined Abhiram and Moataz's definitions into a detailed project flow, with steps describing data sources, example workflow indicators, proposed machine learning extension. 
* Moataz Saadeldin (Product): Summarized interview findings, defined MVP requirements, wrote the NLP data/model plan, and added the baseline schedule risk scoring script. (evidence: #4, PR #5)

## Lean canvas changes 

* Main focus for project is on workload risk awareness for UMD CS/STEM students, not general course recommendation.
* The value proposition shifted toward explaining why a schedule is risky using workload factors such as projects, exams, time commitment, and professor/course-structure uncertainty.
* The main product risk is incomplete or outdated workload data because course structure can change by professor and semester.
