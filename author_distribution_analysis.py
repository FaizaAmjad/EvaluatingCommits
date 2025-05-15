import os
import json
import pandas as pd
from collections import Counter
from tqdm import tqdm

# === CONFIG ===
DATASET_DIR = "DevGPT_Commit_Dataset"
VALID_EXT = ".json"

# === COLLECT JSON FILE PATHS RECURSIVELY ===
json_files = []
for root, _, files in os.walk(DATASET_DIR):
    for file in files:
        if file.endswith(VALID_EXT):
            json_files.append(os.path.join(root, file))

print(f"Found {len(json_files)} JSON files.")

# === COUNT AUTHORS ===
author_counter = Counter()
commit_count = 0

json_files = ["filtered_commits.json"]

for path in tqdm(json_files, desc="Processing files"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {path}: {e}")
                continue

        for item in content:
            author = item.get("Author", "")
            if author:
                author_counter[author] += 1
                commit_count += 1
            else:
                print("something went wrong")
        else:
            print(f"⚠️ Unexpected JSON format in {path}")

    except Exception as e:
        print(f"⚠️ Error reading {path}: {e}")

# === CONVERT TO PANDAS DATAFRAME ===
author_stats = pd.DataFrame(author_counter.items(), columns=["author", "commits"])
author_stats["fraction"] = author_stats["commits"] / commit_count
author_stats = author_stats.sort_values(by="commits", ascending=False).reset_index(drop=True)

# === DISPLAY AND SAVE ===
print(f"\nTotal commits: {commit_count}")
print("\nTop 20 authors:")
print(author_stats.head(20))

# Save to CSV for inspection or stratified sampling planning
author_stats.to_csv("author_distribution.csv", index=False)
print("\nSaved author distribution to author_distribution.csv")
