---

team: TerpLoad
week: 04
date: 2026-06-24
members:

* name: Abhiram Metuku
  github: "@abhimet"
  hat: Data&Eval
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

## Shipped this week

Opened a pull request converting the interview findings into clearer product direction for TerpLoad, including a user research summary, MVP requirements, and an NLP data/model plan. Evidence: #4, PR #5.

Added a simple baseline schedule risk scoring script in `src/risk_rules.py` to give the team a starting point before building the NLP model. Evidence: #4, PR #5.

## User / validation learning

From the 4 student interviews, we learned that the main pain is usually not one hard class by itself, but the way multiple difficult courses stack together in the same semester.

Students currently rely on friends, PlanetTerp, Reddit, and professor information, but this information can be incomplete, outdated, or specific to one professor or semester.

The most important missing information is project workload, exam difficulty, weekly time commitment, and course structure changes.

## Metrics snapshot

* Interviews analyzed: 4
* Repeated course-combination pain pattern: 4/4 interviews
* Baseline risk logic: created initial rule-based version

## Challenges / blockers

We still need reliable course review text and enough labeled examples to train an NLP model.

Course workload can change by professor, semester, and course structure, so TerpLoad should include confidence or uncertainty instead of giving an unsupported answer.

We need to decide which UMD CS/STEM courses to collect data for first.

## Next week's goal

Collect initial course review/course description data for selected UMD CS/STEM courses and create a small labeled dataset for workload signals such as project-heavy, exam-heavy, lab-heavy, writing-heavy, and time-consuming.

## Individual contributions

Abhiram Metuku (Data&Eval): Defined the initial workload labeling guidelines for TerpLoad and began turning the project into an evaluatable NLP task by identifying workload labels such as project-heavy, exam-heavy, homework-heavy, time-consuming, unclear structure, and professor dependency. Evidence: PR #6.

Sriram Vema (Engineering): To be updated after teammate review. Evidence: TBD.

Moataz Saadeldin (Product): Summarized interview findings, defined MVP requirements, wrote the NLP data/model plan, and added the baseline schedule risk scoring script. Evidence: #4, PR #5.

## Lean canvas changes

The project direction is now focused on workload risk awareness for UMD CS/STEM students, not general course recommendation.

The value proposition shifted toward explaining why a schedule is risky using workload factors such as projects, exams, time commitment, and professor/course-structure uncertainty.

The main product risk is incomplete or outdated workload data because course structure can change by professor and semester.
