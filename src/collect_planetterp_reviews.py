"""
need small set of planetterp reviews for TERPLOAD

- need course ids from initial course list csv file
- calls planetterp course API with reviews=True
- waits between calls(api rules say dont hammer w requests)
- Saves raw API responses to data/cache/planetterp/
- Writes a review text CSV to labaeled_reviews.csv
"""
import csv 
import json
import time
