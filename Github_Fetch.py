import requests
import json
import os
from dotenv import load_dotenv
import re
import warnings
import datetime
import time

#######################################################################
# Global Variables

VERBOSE = True
AmountOfCommitsToProcess = 1
SAVE_TO_DISK = False


#######################################################################
# Functions

def FormatUrl(url: str) -> str:
    """
    Converts a GitHub web commit URL to its corresponding API URL.
    If the input is already an API URL, it returns it unchanged.
    If if fails, it returns an exception
    """
    # If already API format, return as-is
    if url.startswith("https://api.github.com/repos/"):
        return url

    # Match web URL like https://github.com/owner/repo/commit/<sha>
    pattern = r"https://github\.com/([^/]+)/([^/]+)/commit/([a-f0-9]{40})"
    match = re.match(pattern, url)

    if match:
        owner, repo, sha = match.groups()
        return f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    else:
        print("Invalid GitHub commit URL format")
        raise ValueError

def reconstruct_from_unified_diff(diff_str: str) -> (str | str):
    """
    Given a unified diff string, returns a tuple (old_file, new_file),
    reconstructing each version line-by-line.
    """
    old_lines = []
    new_lines = []
    total_adds = 0
    total_dels = 0
    hunk_header = re.compile(r'^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@')

    for raw_line in diff_str.splitlines(keepends=True):
        # Skip file header lines
        if raw_line.startswith('--- ') or raw_line.startswith('+++ '):
            continue
        # Skip hunk headers
        if hunk_header.match(raw_line):
            continue

        marker = raw_line[:1]
        content = raw_line[1:]

        if marker == ' ':        # context line
            old_lines.append(content)
            new_lines.append(content)
        elif marker == '-':      # removed from old
            old_lines.append(content)
            total_dels += 1
        elif marker == '+':      # added to new
            new_lines.append(content)
            total_adds += 1
        elif raw_line.startswith('\\'):  
            # “\ No newline at end of file” — strip trailing newline
            if old_lines:
                old_lines[-1] = old_lines[-1].rstrip('\n')
            if new_lines:
                new_lines[-1] = new_lines[-1].rstrip('\n')
        else:
            # any other lines (shouldn’t happen in a well-formed diff)
            continue

    return ''.join(old_lines), ''.join(new_lines), total_dels, total_adds


#######################################################################
# Main 

def main():

    # Load .env file
    load_dotenv()

    # Load existing bad URLs as a dict
    bad_urls_file = "bad_urls.json"

    if os.path.exists(bad_urls_file):
        with open(bad_urls_file, "r") as f:
            try:
                bad_urls = json.load(f)
            except json.JSONDecodeError:
                bad_urls = {}
    else:
        bad_urls = {}

    # load the json and put it in the variable "filteredJson"
    with open('filtered_commits.json', 'r', encoding='utf-8') as f:
        filteredJson = json.load(f)
        if VERBOSE:
            print("loaded JSON")

     # get authentication token from .env
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}"
    } if token else {}

    if not token:
        warnings.warn("WARNING: GitHub token not found. Requests may be rate-limited or unauthorized.")

    seen_shas = set()
    i = 0
    # loop each commit in the Json 
    for commit in filteredJson:
        #if i >= AmountOfCommitsToProcess:
         #   break

        if VERBOSE:
            print("Processing file: " + str(i))
        URL = commit['URL']
        SHA = commit['Sha']
        message = commit['Message']

        if SHA in seen_shas:
            continue
        seen_shas.add(SHA)

        try:
            newURL = FormatUrl(url=URL)
            data = None #clear old data

            try:
                response = requests.get(url=newURL, headers=headers)
                # Check for rate limit error
                if response.status_code == 429:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    current_time = int(datetime.datetime.now().timestamp())
                    wait_time = reset_time - current_time + 1  # Add buffer time
                    print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                    time.sleep(wait_time)  # Wait before retrying
                    continue  # Retry the request

                if response.status_code == 200:
                    data = response.json()
                elif response.status_code == 404:
                    print(f"[404 Not Found] Commit not found: {newURL}")
                    if SHA not in bad_urls:
                        bad_urls[SHA] = URL
                        with open(bad_urls_file, "w") as f:
                            json.dump(bad_urls, f, indent=2)
                    continue  # Skip this commit
                else:
                    print(f"[HTTP {response.status_code}] Failed to fetch: {newURL}")
                    continue
            except requests.RequestException as e:
                print(f"[Request Exception] {e} for URL: {newURL}")
                continue

            if not data:
                continue # Don't proceed with invalid data

            files = data.get("files", [])
            if not files:
             print(f"No files found for commit SHA: {SHA}")
             continue
            code_diffs = []

                # List of path patterns to exclude
            excluded_dirs = [
                "node_modules/", "venv/", "env/", "site-packages/", "__pycache__/",
                "lib/", "target/", "build/", "vendor/bundle/", ".bundle/", "gems/",
                "vendor/", ".cargo/", "go/pkg/", "go/bin/", "go/pkg/mod/",
                "packages/", "bin/", "obj/", ".nuget/", "_build/", "deps/",                ".stack-work/", "dist-newstyle/", ".build/", ".deno/", "Package.resolved"
            ]

            # List of file extensions to exclude
            excluded_files = [".gitignore", ".xml", ".md",".yaml", ".yml" ]

            def is_excluded_path(path):
             # Check if the path includes any excluded directories
             if any(part in path for part in excluded_dirs):
                 return True
             # Check if the file has an excluded extension
             if any(path.endswith(ext) for ext in excluded_files):
                 return True
             # Check if the filename starts with a dot (hidden files)
             if os.path.basename(path).startswith('.'):
                 return True
             return False

            j = 0
            for file in files:
                j += 1
                filename = file["filename"]
                    
                if is_excluded_path(filename):
                    #if VERBOSE:
                        #print(f"Skipping excluded path: {filename}")
                    continue

                if "patch" not in file:
                    continue  # skip binary or unchanged files

                old, new, total_dels, total_adds = reconstruct_from_unified_diff(file['patch'])

                code_entry = {
                    "filename": file["filename"],
                    "before": old,
                    "after": new,
                    "total_deletions": total_dels,
                    "total_additions": total_adds
                }

                code_diffs.append(code_entry)

                # Path to the existing structured commit file
                json_path = os.path.join("Structured_Refactoring_Commits", f"{SHA}.json")

                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        structured_data = json.load(f)
                else:
                    structured_data = {
                        "sha": SHA,
                        "url": URL
                    }

                # Update or create the "code" field as a list
                structured_data["code"] = code_diffs

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(structured_data, f, indent=2)

                if VERBOSE:
                    print(f"Updated structured commit at: {json_path} with {len(code_diffs)} file(s)")

                print(f"number of files in commit with SHA \"{SHA}\" :" + str(j))
        
        except ValueError as error:
            print(f"Failed to format URL: {URL}")
            print(f"error: {error}")
            if SHA not in bad_urls:
                bad_urls[SHA] = URL
                with open(bad_urls_file, "w") as f:
                    json.dump(bad_urls, f, indent=2)
            
        i += 1

if __name__ == "__main__":
    main()