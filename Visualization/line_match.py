import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json

# Load data
df = pd.read_csv('./evaluation_results.csv')
with open('valid_shas.json') as f:
    valid_shas = json.load(f)

# Filter DataFrame to include only SHAs that we manually inspected and found valid
df = df[df['sha'].isin(valid_shas)]

# Check which SHAs are missing from the data
actual_shas = set(df['sha'].unique())
expected_shas = set(valid_shas)

missing_shas = expected_shas - actual_shas

if missing_shas:
    print(f"Missing {len(missing_shas)} SHAs from data:")
    for sha in sorted(missing_shas):
        print(sha)
else:
    print("All SHAs found in the data.")
    
# Shorten SHAs for display
df['short_sha'] = df['sha'].apply(lambda x: x[:7])

# Group by commit (sha)
commit_avg = df.groupby('short_sha')[['crystalbleu_after_vs_chatgpt', 'line_match_after_vs_chatgpt']].mean().reset_index()

# Optional: add number of files per commit (for point size)
commit_avg['file_count'] = df.groupby('short_sha')['file'].count().values

# Plot
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=commit_avg,
    x='line_match_after_vs_chatgpt',
    y='crystalbleu_after_vs_chatgpt',
    size='file_count',
    hue='file_count',  # or change to another variable
    sizes=(50, 300),
    palette='viridis',
    legend='brief'
)

plt.title('CrystalBLEU vs. Line Match per Commit', fontsize=14)
plt.xlabel('Average Line Match')
plt.ylabel('Average CrystalBLEU')
plt.tight_layout()

# Save PDF
output_dir = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, 'crystalbleu_vs_linematch_per_commit.pdf'), format='pdf')
plt.savefig(os.path.join(output_dir, 'crystalbleu_vs_linematch_per_commit.png'), format='png')

plt.show()
