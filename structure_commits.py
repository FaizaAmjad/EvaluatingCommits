import json
import os

# Load the main input file that contains all refactoring commits
with open("filtered_commits.json", "r", encoding="utf-8") as f:
    data = json.load(f)  # 'data' is a list of commits, each commit is a dictionary


# Set the output folder name where we'll save the structured commit files
output_folder = "Structured_Refactoring_Commits"
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't already exist

file_count = 0  # Initialize file counter

# Loop through each commit in the list
for commit in data:
   
    sha = commit.get("Sha")  # Unique identifier for the commit
    chatgpt_sharing_list = commit.get("ChatgptSharing", [])

   # Process each ChatGPT sharing in the list
    for j, sharing in enumerate(chatgpt_sharing_list):
        structured_commit = {
            "sha": sha,
            "url": commit.get("URL"),
            "message": commit.get("Message"),
            "code": {
                "before": "",  # PLACEHOLDER- ADJUST LATER
                "after": ""    # PLACEHOLDER- ADJUST LATER
            },
            "chatgpt_sharing": {
                "title": sharing.get("Title"),
                "url": sharing.get("URL"),
                "number_of_prompts": sharing.get("NumberOfPrompts"),
                "conversations": []
            }
        }

        # Loop through each conversation related to the commit
        conversations = sharing.get("Conversations", [])
        for i, conv in enumerate(conversations):
            structured_commit["chatgpt_sharing"]["conversations"].append({
                "prompt_id": f"{sha}_s{j+1}_p{i+1}",
                "prompt": conv.get("Prompt"),
                "answer": conv.get("Answer"),
                "list_of_code": conv.get("ListOfCode", [])
            })

        # Define the output path: one JSON file per commit sharing, named with SHA + index
        output_path = os.path.join(output_folder, f"{sha}_sharing{j+1}.json")

        # Save the structured commit as a JSON file
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(structured_commit, out_f, indent=2)


        file_count += 1  # Increment counter

    # ✅ Print how many files were created
    print(f"✅ {file_count} JSON files created in '{output_folder}'")
