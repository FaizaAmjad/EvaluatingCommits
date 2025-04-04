import json
import glob
import re
import os

# Define the keywords for each category
fix_keywords = ['fix', 'bug', 'patch', 'resolve', 'correction', 'error']
update_keywords = ['update', 'improve', 'upgrade', 'enhance', 'refine']
refactor_keywords = ['refactor','refactored', 'optimize', 'clean', 'restructure', 'reorganize']

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

# Loop through each file and process the commit messages
for file in json_files:
    with open(file, 'r') as f:
        data = json.load(f)
        
        # Loop through each source (commit)
        for source in data.get("Sources", []):
            commit_message = source.get('Message', '').lower()  # Get the commit message
            print(f"Commit message: {commit_message}")
            
            # Check if the message contains any keyword
            contains_keyword = False

            # Check for keywords in the commit message
            for keyword in fix_keywords + update_keywords + refactor_keywords:
                if keyword in commit_message:
                    contains_keyword = True
                    break  # No need to check further if one keyword is found

            # If any keyword is found, add this commit object to the filtered list
            if contains_keyword:
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
