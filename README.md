# Refactoring With ChatGPT: Evaluating Human Responses to LLM Refactoring Suggestions


Bachelor Thesis in Software Engineering and Management.

This thesis explores how software developers respond to ChatGPT's suggestions for refactoring code. By analyzing commit histories from the  [DevGPT dataset](https://github.com/NAIST-SE/DevGPT), we evaluate the practical usage of LLM-generated refactoring suggestions.

## DevGPT Commit Dataset

This folder (`DevGPT_Commits_Dataset/`) contains commit history data from the [DevGPT GitHub repository](https://github.com/NAIST-SE/DevGPT), sourced from [Zenodo Record 8304091](https://zenodo.org/records/8304091). All HTML content has been removed from the dataset to reduce storage size.

### Contents

- `DevGPT_Commit_Dataset/`: Raw commit data in JSON format.
    - `remove_htmlcontent.py`: Removes HTML content from raw data
- `keyword_analysis.py`: Extracts, cleans,and analyzes commit messages from JSON files to find and save frequent improtant words.
      `word_frequencies.csv` : All words used in commit messages with their frequencies.
- `final_keywords_extraction.py`: Combines keywords from commits and literature, checks matches, fills in missing ones using word frequency, and saves the final list.
      `final_refactoring_keywords.csv`: Output of extracted keywords from dataset (keywords_commit_dataset.csv) and literature (keywords_literature.csv)
- `extract_refactoring_commits.py`: Script to extract unique commit objects with refactoring-related terms
      `filtered_commits.json` : Filtered commit objects containing refactoring keywords.
- `structure_commits.py`: Structures refactoring commit data into a new format for data analysis.
      `Structured_refactoring_commits` : A output folder contaning all commit files under the name of their SHA key.
- `Github_Fetch.py`: Fetches committed code from github repository and  contributes to fill "Structured_refactoring_commits" dataset with following attributes;
    -Code[
          - Files'name
          - Before 
          - After 
          - Number of additions
          - Number of deletions
    ]
- `process_commits.py`: It processes commit data from JSON files, calculates CrystalBLEU, line match scores, and developer-GPT change scores, then saves the results to a CSV file- carries out all comparison and evaluation procedures.
    - `utils/`:  contains helper modules for analyzing code using n-grams and for tokenizing source code.
      - `ngrams_analysis.py`:It collects frequently repeated n-grams (word patterns) from the dataset.
      - `tokenization.py`:Preprocesses code by stripping comments, tokenizing, and extracting n-grams.
    - `evaluate_crystalbleu.py`: Finds which AI-generated code is most similar to the final code by comparing words and skipping common ones.
    - `evaluate_dev_gpt_score.py`: This code checks how much of the new code written by the developer is similar to the AI’s suggestion. It compares lines from the final version with both the original and AI-generated versions. It calculates two scores, one for how much the developer changed on their own and how much the developer reused from the AI’s code.
    - `evaluate_line_match.py`: This code compares lines between AI code and commited code and returns the percentage of exact matches.
    - `evaluation_results.csv`: It shows evaluation results.

## Dependencies

#### Install the necessary Python packages:

```pip install pandas matplotlib nltk```

#### Install CrystalBLEU packages:

```pip install crystalbleu```

#### GitHub Token

```Github_Fetch.py``` requires a GitHub personal access token to access commit details.
You can set it using a [Personal Access Token (PAT)](https://github.com/settings/tokens).

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
9. Run comparisons crystalBLEU, line match and dev_gpt_score and create the evaluation results CSV ``` python process_commits.py```
10. View results in ``` evaluation_results.csv```

## Results
Our analysis showed that:

- 
- 
- 

ATTACH SCREENSHOTS

## Future Work
These are potential areas that future work and studies can be based upon. Our research provides a strong basis for further studies in several areas- some of them are listed below:
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
