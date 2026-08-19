<img width="1206" height="1131" alt="image" src="https://github.com/user-attachments/assets/263b0418-7b94-4049-beb3-200db317b834" />
# TerpLoad
Terpload is a course planning tool for UMD students, mainly for CS/STEM students that analyzes student course reviews with a fine-tuned DistilBERT multi-label classifier and turns review-level workload predictions into an explainable schedule-level report.

Essentially, students begin by selecting 1-6 courses and receive information about:
- overall schedule risk and or uncertainty(based on review coverage)
- confidence level of the report
- main workload driver
- actionable best move
- signals for project-heavy, exam-heavy, time-consuming, homework-heavy
- percentage of reviews supporting each signal
- recent professor context (context only, does not affect workload classification)
- historical grade distributions(context only, does not affect workload classification)

## Problem and Users
Currently, students are able to find information about individual courses through sources such as PlanetTerp, Reddit, friends, GroupMe conversations, and academic advisor. The real problem arises when they cannot determine how the level of workloads of several planned courses can stack together during a semester.

TerpLoad is designed for UMD CS and STEM students planning workload-heavy course combinations, including students who are entering more demanding major courses or balancing several required courses at once.

Early interviews with few students helped establish that the difficulty of a semester came from the combinations of different courses rather than one course alone. 


## How TerpLoad works


```text
Student selects 1–6 courses
            |
            v
     Course profile exists?
        /           \
      yes            no
       |              |
       |       Fetch PlanetTerp reviews
       |              |
       |       Saved DistilBERT model
       |              |
       |       Review-level predictions
       |              |
       |       Course-level aggregation
       |              |
       |          Cache profile
        \            /
         \          /
            |
            v
     Course workload signals
            |
            v
   Transparent schedule rules
            |
            v
      Streamlit report
````


---

## Running TerpLoad Locally

### 1. Clone the Repository

```bash
git clone https://github.com/moatazsaad/msml641-project 
cd https://github.com/moatazsaad/msml641-project
```

### 2. Download Git LFS Model Files

The saved DistilBERT model is stored using Git LFS.

```bash
git lfs install
git lfs pull
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

---
