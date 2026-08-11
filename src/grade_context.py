"""
aggregates grade data 
"""


GRADE_GROUPS = {
    "A": ["A+", "A", "A-"],
    "B": ["B+", "B", "B-"],
    "C": ["C+", "C", "C-"],
    "D": ["D+", "D", "D-"],
}

def aggregate_grade_rows(grade_rows: list[dict]):
  if not grade_rows:
    return None
  counts = {
    "A+": 0, "A": 0, "A-": 0,
    "B+": 0, "B": 0, "B-": 0,
    "C+": 0, "C": 0, "C-": 0,
    "D+": 0, "D": 0, "D-": 0,
    "F": 0,"W": 0,
  }
  for row in grade_rows:
    for grade in counts:
      counts[grade] += int(row.get(grade, 0) or 0)
  
  total = sum(counts.values())
  
  if total == 0:
    return None
  
  def rate(grades):
    return sum(counts[grade] for grade in grades) / total
  return {
    "total_grade_records": total,
    "a_range_rate": rate(GRADE_GROUPS["A"]),
    "b_range_rate": rate(GRADE_GROUPS["B"]),
    "c_range_rate": rate(GRADE_GROUPS["C"]),
    "d_range_rate": rate(GRADE_GROUPS["D"]),
    "f_rate": counts["F"] / total,
    "withdrawal_rate": counts["W"] / total,
    "distribution": counts,
    }