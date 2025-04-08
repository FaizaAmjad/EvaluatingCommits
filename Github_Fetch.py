import requests
import json
import os
from dotenv import load_dotenv
import re

#######################################################################
# Global Variables

VERBOSE = True
AmountOfCommitsToProcess = 1

#######################################################################
# Functions

def FormatUrl(url: str) -> str:
    """
    Converts a GitHub web commit URL to its corresponding API URL.
    If the input is already an API URL, it returns it unchanged.
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
        return None

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

    if token:
        headers = {
            "Authorization": f"token {token}"
        }
    else:
        headers = {}
        print("WARNING, authentication not working. Ensure .env file is used with a 'GITHUB_TOKEN'")


    i = 0
    # loop each commit in the Json 
    for commit in filteredJson:
        if i >= AmountOfCommitsToProcess:
            break

        if VERBOSE:
            print("Processing file: " + str(i))
        URL = commit['URL']
        SHA = commit['Sha']
        message = commit['Message']
        #print(str(i) + ": " + message)

        newURL = FormatUrl(url=URL)

        if newURL is None:
            print(f"Failed to format URL: {URL}")
            if SHA not in bad_urls:
                bad_urls[SHA] = URL
                with open(bad_urls_file, "w") as f:
                    json.dump(bad_urls, f, indent=2)
        else:
            try:
                response = requests.get(url=newURL, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print(f"Request failed with status: {response.status_code} for URL: {newURL}")
            except requests.RequestException as e:
                print(f"Request error: {e}")

            if data:
                files = data.get("files", [])
                listOfMentionedFiles = []


                for file in files:
                    '''
                    --- File ---
                    "sha": str (unique)
                    "filename": str
                    "status": str
                    "additions": int
                    "deletions": int
                    "changes": int (sum of add and del)
                    "blob_url": str
                    "raw_url": str
                    "contents_url": str
                    '''
                    fileName = file['filename']

                    #TODO: somehow compare all these "file" objects with the converstations in the "commit" objects.
                    # Use a similarity comparison.

                    #TODO: potential performance issues with brute force, maybe find a way to see if there are any files that are not related to the conversations
                    
                    if VERBOSE:
                        print(f"File: {fileName}")
                        print(f"Changes: +{file['additions']} -{file['deletions']}")

            
        i += 1

if __name__ == "__main__":
    main()