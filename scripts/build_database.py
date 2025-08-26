import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
import time
from datetime import datetime
import argparse
import os

# Settings
DATABASE_DIRC = "database"
BASE_URL = "http://export.arxiv.org/api/query"
# CATEGORIES = ["astro-ph.HE", "astro-ph.GA", "astro-ph.CO", "astro-ph.EP", "astro-ph.IM", "astro-ph.SR",
#               "astro-ph.*", "cond-mat.*", "hep-*", "nucl-*", "cs.*"]
# START_YEAR = 2019
# END_YEAR = 2025
CATEGORIES = ["cs.*"]
START_YEAR = 2022
END_YEAR = 2022
MAX_RESULTS_PER_MONTH = 250
RESULTS_PER_REQUEST = 250
TARGET_WORDS = ["leverag", "robust", "novel", "utiliz", "paradigm", "comprehensive", "boast", "convey",
                "driven by", "insight", "pivotal", "framework", "scalable", "rigorous", "in-depth",
                "systematic", "state-of-the-art", "groundbreaking", "promising", "remarkable", "delv",
                "intricate", "valuable", "exceptional", "notabl", "innovative", "primarily", "critical",
                "thoroughly", "subsequently", "particularly", "thereby", "significant", "foster",
                "crucial", "effectively", "additionally", "enhance", "capabilities", "paramount",
                "vital", "uncover", "unveil", "untangle", "albeit", "endeavor", "herein", "show",
                "small", "find", "help", "discover", "look", "need", "change", "make", "thing"]


def main():
    os.makedirs(DATABASE_DIRC, exist_ok=True)
    extract_data()


def get_quarter(date_str):
    dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
    quarter = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{quarter}"


def fetch_abstracts(year, quarter, category):
    month_start = (quarter - 1) * 3 + 1
    month_end = month_start + 2
    entries = []
    for month in range(month_start, month_end + 1):
        start_date = f"{year}{month:02d}010000"
        end_date = f"{year}{month:02d}312359"
        for start in range(0, MAX_RESULTS_PER_MONTH, RESULTS_PER_REQUEST):
            query = f"search_query=cat:{category}+AND+submittedDate:[{start_date}+TO+{end_date}]"
            url = f"{BASE_URL}?{query}&start={start}&max_results={RESULTS_PER_REQUEST}"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                root = ET.fromstring(response.text)
                new_entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                if not new_entries:
                    break
                entries.extend(new_entries)
                time.sleep(2)
            except Exception as e:
                print(f"Error fetching {year} month {month}: {e}")
                break
    return entries


def extract_data():
    for category in CATEGORIES:
        print(f"--------{category_name(category)}--------")
        quarter_data = defaultdict(lambda: defaultdict(lambda: {"count_words": 0, "count_abstracts": 0, "total_abstracts": 0}))
        for year in range(START_YEAR, END_YEAR + 1):
            for quarter in range(1, 5):
                if year == 2025 and quarter > 2:
                    break
                print(f"Processing {year} Q{quarter}...")
                entries = fetch_abstracts(year, quarter, category)
                for entry in entries:
                    summary = entry.find("{http://www.w3.org/2005/Atom}summary")
                    published = entry.find("{http://www.w3.org/2005/Atom}published")
                    if summary is not None and published is not None:
                        abstract = summary.text.lower() if summary.text else ""
                        quarter_label = get_quarter(published.text)
                        for word in TARGET_WORDS:
                            count = abstract.count(word.lower())
                            quarter_data[quarter_label][word]["count_words"] += count
                            if count > 0:
                                quarter_data[quarter_label][word]["count_abstracts"] += 1
                            quarter_data[quarter_label][word]["total_abstracts"] += 1
        save_csv(quarter_data, category)


def save_csv(quarter_data, category):
    # filename = os.path.join(DATABASE_DIRC, f"data_{category_name(category)}.csv")
    filename = os.path.join(DATABASE_DIRC, f"_data_{category_name(category)}.csv")
    rows = []
    for quarter in sorted(quarter_data.keys()):
        for word in TARGET_WORDS:
            c = quarter_data[quarter][word]
            avg1 = c["count_words"] / c["total_abstracts"] if c["total_abstracts"] > 0 else 0
            avg2 = c["count_abstracts"] / c["total_abstracts"] if c["total_abstracts"] > 0 else 0
            rows.append({
                "Quarter": quarter,
                "Word": word,
                "Word Count": c["count_words"],
                "Abstact Count": c["count_abstracts"],
                "Total Abstracts Read": c["total_abstracts"],
                "Average per Abstract": avg1,
                "Ratio of Abstracts": avg2 
            })
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")
    return df


def category_name(category):
    from copy import deepcopy
    category_name = deepcopy(category)
    if category_name.endswith("*"):
        category_name = category_name[:-1]
    if category_name.endswith(".") or category_name.endswith("-"):
        category_name = category_name[:-1]
    return category_name


if __name__ == "__main__":
    main()
