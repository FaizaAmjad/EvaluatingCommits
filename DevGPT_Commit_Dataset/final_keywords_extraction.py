import csv

def generate_final_csv(commit_file, literature_file, word_frequency_file, output_file):
    # Read commit keywords
    final_keywords = {}  # {word: frequency}
    commit_keywords_set = set()  # to check matches
    
    with open(commit_file, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 3:
                word = row[1].strip().lower()
                try:
                    freq = int(row[2])
                    final_keywords[word] = freq
                    commit_keywords_set.add(word)
                except ValueError:
                    continue

    # Read word frequencies
    word_frequencies = {}
    with open(word_frequency_file, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                word = row[0].strip().lower()
                try:
                    freq = int(row[1])
                    word_frequencies[word] = freq
                except ValueError:
                    continue

    # Read literature keywords
    matched_literature_keywords = []
    unmatched_literature_keywords = []
    
    with open(literature_file, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                word = row[0].strip().lower()
                if word in commit_keywords_set:
                    matched_literature_keywords.append(word)
                else:
                    freq = word_frequencies.get(word, 0)
                    final_keywords[word] = freq
                    unmatched_literature_keywords.append(word)


    # Read synonym keywords (from keywords_synonyms.csv)
    with open('keywords_synonyms.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                word = row[0].strip().lower()
                if word in commit_keywords_set:
                    matched_literature_keywords.append(word)
                else:
                    freq = word_frequencies.get(word, 0)
                    final_keywords[word] = freq
                    unmatched_literature_keywords.append(word)
                

    # Write to output CSV
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Keyword", "Frequency"])
        for word, freq in final_keywords.items():
            writer.writerow([word, freq])

    # Write unmatched commit keywords
    unmatched_commit_keywords = sorted([kw for kw in commit_keywords_set if kw not in matched_literature_keywords])
    with open("unmatched_commit_keywords.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Unmatched Commit Keyword", "Frequency"])
        for word in unmatched_commit_keywords:
            freq = final_keywords.get(word, 0)
            writer.writerow([word, freq])

    # Print summary
    print(f"✅ Final list written to: {output_file}")
    print(f"🔍 {len(matched_literature_keywords)} literature keywords matched commit keywords:")
    print(sorted(matched_literature_keywords))

    print(f"\n➕ {len(unmatched_literature_keywords)} literature keywords added from frequency list or defaulted to 0:")
    print(sorted(unmatched_literature_keywords))

    # Optional: commit keywords not found in literature
    unmatched_commit_keywords = sorted([kw for kw in commit_keywords_set if kw not in matched_literature_keywords])
    print(f"\n❌ {len(unmatched_commit_keywords)} commit keywords NOT found in literature:")
    print(unmatched_commit_keywords)

# Run the function
generate_final_csv(
    commit_file='keywords_commit_dataset.csv',
    literature_file='keywords_literature.csv',
    word_frequency_file='word_frequencies.csv',
    output_file='final_refactoring_keywords.csv'
)
