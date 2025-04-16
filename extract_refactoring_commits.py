import json
import glob
import re
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import csv

nltk.download('punkt_tab')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Function to read keywords from the final list CSV
def read_keywords_from_csv(filename):
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return {row[0].strip().lower() for row in reader if row}  # Return a set of keywords

# File path to the final list of keywords (created previously)
keywords_file = 'final_list_of_keywords.csv'

# Read keywords from the final list of keywords CSV
keywords = read_keywords_from_csv(keywords_file)

# Lemmatize the keywords
lemmatized_keywords = set(lemmatizer.lemmatize(kw) for kw in keywords)

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

# Initialize counters
total_commits = 0
filtered_refactoring_commits = 0

# Process commit messages
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)

        for source in data.get("Sources", []):
            total_commits += 1  # Increment total commits count
            commit_message = source.get('Message', '').lower()

            # Tokenize and lemmatize the commit message
            tokens = word_tokenize(commit_message)
            lemmatized_tokens = set(lemmatizer.lemmatize(token) for token in tokens)

            # Check if any keyword is in the lemmatized tokens
            if lemmatized_keywords.intersection(lemmatized_tokens):
                filtered_commits.append(source)
                filtered_refactoring_commits += 1  # Increment filtered refactoring commits count


# Save the filtered commits to a new JSON file
with open(output_file, 'w') as out_file:
    json.dump(filtered_commits, out_file, indent=2)

print(f"✅ Filtered commits saved!")

# Print the number of commits processed and filtered
print(f"Total number of commits processed: {total_commits}")
print(f"Total number of filtered refactoring commits: {filtered_refactoring_commits}")