import json
import csv

# Input JSON file
json_file = 'filtered_commits.json'

# Output CSV files
messages_csv = 'filtered_commit_messages.csv'

# Load the JSON data
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare rows for both CSVs
message_rows = []

for idx, commit in enumerate(data, start=1):
    message = commit.get('Message', '')
    message_rows.append({'CommitIndex': f'COMMIT {idx}', 'Message': message})

# Write commit messages
with open(messages_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['CommitIndex', 'Message'])
    writer.writeheader()
    writer.writerows(message_rows)

print(f"✅ Commit messages exported to {messages_csv}")
