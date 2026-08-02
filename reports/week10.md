team: TerpLoad
week: 10
date: 2026-08-05

members:
- Moataz Abdelaziz — @moatazsaad — Product
- Abhiram Metuku — @abhimet — Data&Eval
- Sriram Vema — @sriramvema — Engineering

## Shipped this week

- Added Week 10 weak-labeled reviews
- Updated TF-IDF evaluation to use 5-fold cross-validation
- Added a low-evidence warning for courses with few reviews
- Updated documentation
- Added tests
- Added a simple Streamlit demo

## Learning

Adding more labeled reviews helped expand the dataset, but the model still struggled with some labels, especially `homework_heavy`.

The current flow is:

cleaned reviews → weak labels → TF-IDF baseline → course signals → CLI / Streamlit report

## Metrics

- Labeled reviews: 104
- Reviews added this week: 40
- Workload labels: 4
- Tests passing: 12/12
- DistilBERT: not used

## Challenges

- The labeled dataset is still small
- Some labels need more examples
- Some MSML courses have very few reviews

## Next week

- Add setup instructions
- Review the Week 10 changes with the team
- Prepare the final demo and report

## Contributions

- Moataz Abdelaziz: Added Week 10 updates, low-evidence warning, tests, docs, and Streamlit demo. Evidence: issue #42, PR #43
- Abhiram Metuku: . Evidence: issue #, PR #
- Sriram Vema:  Evidence: issue #, PR #