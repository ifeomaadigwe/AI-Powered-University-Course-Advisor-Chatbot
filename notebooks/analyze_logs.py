import os
from collections import Counter

def parse_log(file_path):
    queries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "User Query" in line:
                q = line.split("User Query:")[-1].strip()
                queries.append(q)
    return queries

log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
all_queries = []

for log in log_files:
    all_queries.extend(parse_log(os.path.join("logs", log)))

print("Top 5 Most Frequently Asked Questions:")
for q, freq in Counter(all_queries).most_common(5):
    print(f"  {q} - {freq} times")