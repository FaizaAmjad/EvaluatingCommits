import os
import json

def remove_html_content_field(obj):
    """Recursively remove 'HTMLContent' fields from nested JSON structures."""
    if isinstance(obj, dict):
        return {
            key: remove_html_content_field(value)
            for key, value in obj.items()
            if key != "HTMLContent"
        }
    elif isinstance(obj, list):
        return [remove_html_content_field(item) for item in obj]
    else:
        return obj

def clean_json_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    data = json.load(infile)

                cleaned_data = remove_html_content_field(data)

                with open(file_path, 'w', encoding='utf-8') as outfile:
                    json.dump(cleaned_data, outfile, indent=4, ensure_ascii=False)

                print(f"Cleaned: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

clean_json_files_in_folder('DevGPT_Commit_Dataset')
