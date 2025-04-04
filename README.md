# EvaluatingCommits : Evaluating Human Responses to LLM Refactoring Suggestions
Bachelor Thesis in Software Engineering and Management.

We will be using DevGPT dataset to evalutate developer's commits where they use ChatGPT's suggestions for refactoring code.

## DevGPT Commit Dataset

This folder (`DevGPT_Commits_Dataset/`) contains commit history data from the [DevGPT GitHub repository](https://github.com/NAIST-SE/DevGPT), sourced from [Zenodo Record 8304091](https://zenodo.org/records/8304091).

### Contents
- `DevGPT_Commit_Dataset.json`: Raw commit data
- `extract_refactoring_commits.py`: Script to extract commit objects with refactoring keywords
- `filtered_commits.json` : Commits objects stored after filtering

### Credits
Data originally compiled by Xiao, T., Treude, C., Hata, H., & Matsumoto, K. (2023). DevGPT: Studying Developer-ChatGPT Conversations [Data set]. Zenodo.

# Requirements
## Install Pandas Matplotlib nltk
- pip install pandas matplotlib nltk
