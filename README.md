# Refactoring With ChatGPT: Evaluating Human Responses to LLM Refactoring Suggestions


Bachelor Thesis in Software Engineering and Management.

This thesis explores how software developers respond to ChatGPT's suggestions for refactoring code. By analyzing commit histories from the  [DevGPT dataset](https://github.com/NAIST-SE/DevGPT), we evaluate the practical usage of LLM-generated refactoring suggestions.

## DevGPT Commit Dataset

This folder (`DevGPT_Commits_Dataset/`) contains commit history data from the [DevGPT GitHub repository](https://github.com/NAIST-SE/DevGPT), sourced from [Zenodo Record 8304091](https://zenodo.org/records/8304091). All HTML content has been removed from the dataset to reduce storage size.

### Contents





- `DevGPT_Commit_Dataset/`: Raw commit data in JSON format
- `Structured_Refactoring_Commits/`: Restructured data of filtered refactoring commits (each file named by its SHA key)
- `filtered_commits.json` : Filtered commit objects containing refactoring keywords
- `extract_refactoring_commits.py`: Script to extract unique commit objects with refactoring-related terms
- `Github_Fetch.py`: Fetches: committed code from github repository
  Contributes: to fill dataset with following attributes
    - Changed files'name
    - Number of additions and deletions
    - Code before and after changes

- `remove_htmlcontent.py`: Removes HTML content from raw data
- `structure_commits.py`: Structures refactoring commit data into a new format for data analysis

## Dependencies

#### Install the necessary Python packages:

```pip install pandas matplotlib nltk```


## Installation

- ```git clone "https://github.com/FaizaAmjad/EvaluatingCommits.git"```
- ```cd EvaluatingCommits```
- Install dependencies (see above)

## How to Run

Run the following script in order:

1. Once the raw data files are in the DevGPT_Commit_Dataset, Clean HTML from data
``` remove_htmlcontent.py```
2. ```cd DevGPT_Commit_Dataset```
3. Analyse words in all commit messages``` python keyword_analysis.py```
4. Once you have edited the - `keywords_literature.csv` and `keywords_synonyms.csv` if required, output a final list of keywords ``` python final_keywords_extraction.py```
5. ```cd ..```
6. Filter a collection of refactoring commits using the refactoring terms ``` python extract_refactoring_commits.py```
7. Structure Filtered Commits ``` python structure_commits.py```
8. Fetch code changes for all commits ``` python Github_Fetch.py```

## GitHub Token

```Github_Fetch.py``` requires a GitHub personal access token to access commit details.
You can set it using a [Personal Access Token (PAT)](https://github.com/settings/tokens).

## Results
Our analysis showed that:

- 
- 
- 

ATTACH SCREENSHOTS

## Future Work
- Use other LLMs to analyse these interactions
- Extend analysis to non-refactoring tasks (e.g., bug fixes or feature additions)

## Contributors
- David Schön 
- Faiza Amjad 
- Tehreem Asif
- Ranim Khojah – Thesis supervision

## License

This project is licensed under ________________________

## Acknowledgements

- This research was conducted at the University of Gothenburg.
- Thanks to the maintainers of the DevGPT dataset for making this work possible.
- Gratitude to our supervisor and peers for their continuous support.

### Credits
Data originally compiled by Xiao, T., Treude, C., Hata, H., & Matsumoto, K. (2023). DevGPT: Studying Developer-ChatGPT Conversations [Data set]. Zenodo.
