import csv

# List of confirmed keywords (duplicates removed)
keywords = list(set([
    "reformat", "Reorganize", "Reorganise", "replace", 
    "reorg", "refactor", "restructure", "optimised", "cleanup", "Improve", 
    "clean", "Refine", "tidy", "enhance", "simplify", "efficient", 
    "reworked", "reduced", "clean-up", "Adjusted", "change", "Rename", 
    "Combine", "Gather", "Inline", "Merge", "Update", "organise", 
    "organize", "uncomment", "rewrite", "flatten", "consolidate", 
    "concise"
]))

# Convert all keywords to lowercase
keywords = [keyword.lower() for keyword in keywords]

# Define the name of the CSV file
csv_filename = "literature_keywords.csv"

# Open the CSV file in write mode and create a CSV writer object
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write each keyword to the CSV file
    for keyword in keywords:
        writer.writerow([keyword])

print(f"CSV file '{csv_filename}' created successfully with the keywords.")
