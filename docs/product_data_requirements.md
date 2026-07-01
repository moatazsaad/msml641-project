# Product Data Requirements

## Goal

TerpLoad needs course related text data that helps predict whether a planned UMD CS/STEM schedule has low, medium or high workload risk.

This supports the MVP:

> A user can enter a planned UMD CS/STEM course schedule and get a Low, Medium, or High workload risk result with the main reasons

## What the data should answer

For each course, the data should help answer:

* Is the course project heavy?
* Is the course exam heavy?
* Is the course homework heavy?
* Is the course lab heavy?
* Is the course writing heavy?
* Is the course time consuming?
* Does workload depend heavily on professor?
* Is the course structure uncertain or different by semester?

## Useful data

* student course reviews
* professor reviews
* course descriptions
* comments about projects, exams, labs, homework and weekly time commitment

## First data source to test

PlanetTerp is the first source to test because it has UMD course and professor review text

Official course descriptions can support the data but they are not enough alone because they do not usually describe real student workload

## Initial courses

The first data sample should focus on:

* CMSC216
* CMSC250
* CMSC330
* CMSC351
* STAT400
* MATH410
* STAT410
* MSML604
* MSML605
* MSML606

## Workload labels

The first NLP model should try to predict:

* project_heavy
* exam_heavy
* homework_heavy
* time_consuming

## Product requirement

TerpLoad should not only give a risk score. It should explain why the schedule may be risky.

Example:

```text
Risk: High
Confidence: Medium

Reasons:
- CMSC330 appears project-heavy.
- CMSC351 appears exam-heavy.
- STAT400 adds more exam pressure.
- Multiple technical courses may stack badly.
```

