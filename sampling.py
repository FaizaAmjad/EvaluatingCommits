import os
import json
import random
from collections import defaultdict, Counter
from tqdm import tqdm

# === CONFIG ===
INPUT_FOLDER = "Structured_Refactoring_Commits"
MAX_COMMITS_PER_AUTHOR = 5 #updated to 5
OUTPUT_FOLDER = "Sampling_And_Manual_Inspection"

# === STEP 1: Load All Commits ===
json_files = []
for root, _, files in os.walk(INPUT_FOLDER):
    for file in files:
        if file.endswith(".json"):
            json_files.append(os.path.join(root, file))

print(f"Found {len(json_files)} commit files.")

commits_by_author = defaultdict(list)

for path in tqdm(json_files, desc="Reading commit files"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            commit = json.load(f)
            author = commit.get("Author") or commit.get("author")
            if author:
                commits_by_author[author].append(commit)
    except Exception as e:
        print(f"⚠️ Failed to load {path}: {e}")

# === STEP 2: Randomly Cap to 5 Commits Per Author ===
random.seed(42)
sampled_commits = []

for author, commits in commits_by_author.items():
    if len(commits) > MAX_COMMITS_PER_AUTHOR:
        sampled = random.sample(commits, MAX_COMMITS_PER_AUTHOR)
    else:
        sampled = commits
    sampled_commits.extend(sampled)

print(f"\nSelected {len(sampled_commits)} commits from {len(commits_by_author)} authors.")





# === Save Filtered Sampled Commits ===
for commit in sampled_commits:
    sha = commit.get("sha")
    if not sha:
        print("Error saving sampled commit")
        continue

    commit_path = os.path.join(OUTPUT_FOLDER, f"{sha}.json")
    try:
        with open(commit_path, "w", encoding="utf-8") as f:
            json.dump(commit, f, indent=2, ensure_ascii=False)
        
    except Exception:
        print(f"failed to save commit: {sha}")
    else:
        print(f"✅ Saved sampled commits to {OUTPUT_FOLDER}")


# === Save List of Sampled SHA Keys ===
sha_list = [commit["sha"] for commit in sampled_commits if "sha" in commit]
with open("sampled_shas.json", "w", encoding="utf-8") as f:
    json.dump(sorted(sha_list), f, indent=2)
print(f"✅ Saved list of {len(sha_list)} SHAs to sampled_shas.json")
