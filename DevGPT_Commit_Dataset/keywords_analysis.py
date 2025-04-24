import glob
import os
import json
import re
import matplotlib.pyplot as plt
from collections import Counter
import nltk
import pandas as pd

from nltk.corpus import stopwords

# Only needed the first time
# nltk.download('stopwords')

# Define paths
folder_path = os.getcwd()
json_files = glob.glob(os.path.join(folder_path, "*.json"))

# Extract commit messages from all JSON files
commit_messages = []

for file in json_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = json.load(f)
        if "Sources" in content:
            for item in content["Sources"]:
                message = item.get("Message", "")
                if message:
                    commit_messages.append(message)

# Preprocess messages
messages = [msg.lower() for msg in commit_messages]

# Clean punctuation, numbers, and short words
cleaned = [re.sub(r'\b\w{1,2}\b', '', msg) for msg in messages]  # remove short words
cleaned = [re.sub(r'[^a-z\s]', '', msg) for msg in cleaned]      # remove punctuation/numbers

# Tokenize and flatten
all_words = ' '.join(cleaned).split()

# Remove stopwords
stop_words = set(stopwords.words('english'))

filtered_words = [
    word for word in all_words
    if word not in stop_words and not word.startswith('http') and not re.match(r'www\.', word)
]

# Count top keywords
word_counts = Counter(filtered_words)

# Get top 15 most common (non-refactoring) keywords
top_common = set(word for word, _ in word_counts.most_common(35))

# Remove them from the count
filtered_word_counts = Counter({word: count for word, count in word_counts.items() 
                                if word not in top_common and count >= 50})

words = filtered_word_counts.most_common()

print("Excluded top common keywords:", top_common)

cleaned_commit_messages = [msg.replace('\n', ' ').replace('\r', '') for msg in commit_messages]

df = pd.DataFrame({
    'commit_number': range(1, len(cleaned_commit_messages) + 1),
    'message': cleaned_commit_messages
})
df.to_csv("all_commit_messages.csv", index=False)


# Save all word frequencies to CSV
all_word_freq_df = pd.DataFrame(word_counts.items(), columns=['word', 'frequency'])
all_word_freq_df = all_word_freq_df.sort_values(by='frequency', ascending=False)
all_word_freq_df.to_csv("word_frequencies.csv", index=False)

# Plot
# keywords, counts = zip(*words)
# plt.figure(figsize=(12, 8))
# plt.barh(keywords[::-1], counts[::-1], color='mediumseagreen')
# plt.title('Top Keywords in Commit Messages')
# plt.xlabel('Frequency')
# plt.tight_layout()

# Save to folder
# output_folder = "visualizations"
# os.makedirs(output_folder, exist_ok=True)
# plt.savefig(os.path.join(output_folder, "demo_plot.png"), bbox_inches='tight')

# plt.show()

