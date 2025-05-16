import os
import json
import random
from collections import defaultdict, Counter
from tqdm import tqdm

# === CONFIG ===
INPUT_FOLDER = "Structured_Refactoring_Commits"
MAX_COMMITS_PER_AUTHOR = 2
RESEARCHERS = ["r1", "r2", "r3"]
ASSIGNMENT_PREFIX = "assigned_shas_"  # Output: assigned_shas_r1.json etc.
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

# === STEP 2: Randomly Cap to 2 Commits Per Author ===
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

# === STEP 3: Assign Each SHA to 2 Researchers ===
shas = [commit["sha"] for commit in sampled_commits if "sha" in commit]
assignments = {r: set() for r in RESEARCHERS}
researcher_load = Counter({r: 0 for r in RESEARCHERS})

for sha in shas:
    # Pick 2 researchers with the least current load
    least_loaded = sorted(RESEARCHERS, key=lambda r: researcher_load[r])
    chosen = random.sample(least_loaded[:2], 2)  # Break ties randomly
    for r in chosen:
        assignments[r].add(sha)
        researcher_load[r] += 1

# === Save Assignment Lists ===
for r in RESEARCHERS:
    path = f"{ASSIGNMENT_PREFIX}{r}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(assignments[r]), f, indent=2)
    print(f"✅ Saved {len(assignments[r])} SHAs to {path}")

# === Final Check: Each SHA assigned to exactly 2 researchers ===
sha_counts = Counter()
for r in RESEARCHERS:
    for sha in assignments[r]:
        sha_counts[sha] += 1

errors = [sha for sha, count in sha_counts.items() if count != 2]
if errors:
    print(f"⚠️ {len(errors)} SHAs were not assigned to exactly 2 researchers.")
else:
    print("✅ All SHAs assigned to exactly 2 researchers.")
