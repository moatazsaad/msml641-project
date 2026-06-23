"""
need small set of planetterp reviews for TERPLOAD

- need course ids from initial course list csv file
- calls planetterp course API with reviews=True
- waits between calls(api rules say dont hammer w requests)
- Saves raw API responses to data/cache/planetterp/
- Writes a review text CSV to data/raw_planetterp.csv
"""
import csv 
import json
import time
from pathlib import Path
from typing import Any 

import requests

BASE_URL = "https://planetterp.com/api/v1/course"
#need cahche so we dont hammer api
COURSE_LIST_PATH = Path("data/initial_course_list.csv")
CACHE_DIR = Path("data/cache/planetterp")
OUTPUT_PATH = Path("data/raw_planetterp_reviews.csv")

def load_course_ids(path:Path) -> list[str]:
  """Load course IDs """