# Refactoring With ChatGPT: Evaluating Human Responses to LLM Refactoring Suggestions


Bachelor Thesis in Software Engineering and Management.

We will be using DevGPT dataset to evalutate developers' commits where they use ChatGPT's suggestions for refactoring code.

## DevGPT Commit Dataset

This folder (`DevGPT_Commits_Dataset/`) contains commit history data from the [DevGPT GitHub repository](https://github.com/NAIST-SE/DevGPT), sourced from [Zenodo Record 8304091](https://zenodo.org/records/8304091). It HTML content for each commit object has been removed from this data to reduce storage used.

### Contents





- `DevGPT_Commit_Dataset`: Folder consisting Raw commit data
- `Structured_Refactoring_Commits`: Folder consisting all filtered refactoring commits within a new data structure- each file refers to a unique commit object labelled with its unique SHA key
- `extract_refactoring_commits.py`: Script to extract unique commit objects with refactoring keywords
- `filtered_commits.json` : Commits objects stored after filtering for refactoring commits
- `Github_Fetch.py`: Program which fetches names of changed files, number of additions, deletions, code before changes and after change for each refactoring commit
- `remove_htmlcontent.py`: Program which removes the html content from DevGPT_Commit_Dataset
- `structure_commits.py`: Program to fetch and store information of each commit within the new data structure for analysis

## Dependencies
### Install Pandas Matplotlib nltk
- pip install pandas matplotlib nltk


## Installation

## How to Run
## GitHub Token
## Results
## Future Work
## Contributors
## License
## Acknowledgements

### Credits
Data originally compiled by Xiao, T., Treude, C., Hata, H., & Matsumoto, K. (2023). DevGPT: Studying Developer-ChatGPT Conversations [Data set]. Zenodo.