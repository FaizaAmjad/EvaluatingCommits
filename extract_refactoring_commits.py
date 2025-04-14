import json
import glob
import re
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

nltk.download('punkt_tab')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Define the keywords for each category
update_keywords = ['update', 'improve', 'upgrade', 'enhance', 'refine', 'modify', 'rewrite', 'simplify']
refactor_keywords = ['refactor', 'optimize', 'clean', 'change', 'rename', 'uncomment', 'replace', 'restructure', 'reorganize', 'organize', 'overwrite', 'regenerate', 'concise', 'revert', 'remove', 'reduce', 'reformat']

# Folder containing the JSON files
folder_path = os.getcwd()
output_file = "filtered_commits.json"

# Find all JSON files in the directory
json_files = glob.glob(os.path.join(folder_path, "DevGPT_Commit_Dataset", "*.json"))

# Debugging: Print the list of found JSON files
print(f"Searching in folder: {folder_path}")
print("Found JSON files:", json_files)

# Check if any files were found
if json_files:
    print(f"Total number of JSON files: {len(json_files)}")
else:
    print("No JSON files found in the directory.")
    
# Initialize a list to store filtered commits
filtered_commits = []

# Combine all keywords
all_keywords = set(update_keywords + refactor_keywords)

# Lemmatize the keywords
lemmatized_keywords = set(lemmatizer.lemmatize(kw.lower()) for kw in all_keywords)

# Process commit messages
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)

        for source in data.get("Sources", []):
            commit_message = source.get('Message', '').lower()

            # Tokenize and lemmatize the commit message
            tokens = word_tokenize(commit_message)
            lemmatized_tokens = set(lemmatizer.lemmatize(token) for token in tokens)

            # Check if any keyword is in the lemmatized tokens
            if lemmatized_keywords.intersection(lemmatized_tokens):
                filtered_commits.append(source)

# Save the filtered commits to a new JSON file
with open(output_file, 'w') as out_file:
    json.dump(filtered_commits, out_file, indent=2)

print(f"✅ Filtered commits saved!")

# Read the output file and count the number of commits
with open(output_file, 'r') as f:
    data = json.load(f)

# If data is a list of commits, you can directly count the length
commit_count = len(data)

# Print the number of commits saved
print(f"Total number of filtered commits saved in the output file: {commit_count}")
