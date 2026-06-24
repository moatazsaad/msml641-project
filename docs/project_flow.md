# Proposed Project Flow

## Overview
TerpLoad is a proposed tool designed to help UMD students evaluate the potential workload of a planned semester schedule. The goal is to combine student feedback, course information, and workload indicators to provide students with a more informed view of their course selections before registration.

## Proposed Workflow

### Step 1: Student Provides Planned Schedule
A student would enter the courses they are considering for an upcoming semester.

Example:
* MSML604
* MSML605

This schedule would serve as the starting point for workload analysis.

### Step 2: Gather Course Information
For each course, TerpLoad would collect information identified during user research and interviews.

Potential data sources include:
- PlanetTerp reviews
- Reddit discussions
- Student surveys

The goal is to combine multiple student perspectives rather than relying on a single source.

### Step 3: Identify Workload Indicators
Course reviews and feedback would be analyzed to identify recurring workload themes.
Example: "Projects took forever and exams were difficult."

Indicators:
- Project-heavy
- Exam-heavy
- Time-consuming

These indicators would help describe the expected workload characteristics of a course.

### Step 4: Estimate Course Workload
Using the collected information, each course could be assigned workload-related attributes such as:

- Project intensity
- Exam intensity
- Grading leniency

These attributes would provide a standardized way to compare courses.

## Proposed Machine Learning Extension
A classifier can analyze the individual reports for sentiment, which we could use to give a more accurate score for each course. This would allow us to build a more reliable metric that students can compare. We can train a multiclass classifier on a list of predetermined attrbutes or indicators so that we can pull them from our sources.
