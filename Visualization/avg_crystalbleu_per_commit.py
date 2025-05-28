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

# Group by SHA and calculate average CrystalBLEU
sha_avg = df.groupby('sha')['crystalbleu_after_vs_chatgpt'].mean().reset_index()

# Replace SHA with simple labels: Commit 1, Commit 2, ...
sha_avg['commit_label'] = [f'Commit {i+1}' for i in range(len(sha_avg))]

# Sort by score
sha_avg = sha_avg.sort_values(by='crystalbleu_after_vs_chatgpt', ascending=False)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(data=sha_avg, x='commit_label', y='crystalbleu_after_vs_chatgpt', palette='Blues_d')

plt.title('Average CrystalBLEU Score per Commit', fontsize=16)
plt.xlabel('Commit', fontsize=12)
plt.ylabel('Average CrystalBLEU', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.xticks([])  # hides x-tick labels
plt.xlabel('')  # removes x-axis label text

# Ensure 'images' folder exists
output_dir = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(output_dir, exist_ok=True)

# Save plot as PDF
output_path = os.path.join(output_dir, 'avg_crystalbleu_per_commit.pdf')
plt.savefig(output_path, format='pdf')

#save plot as png
plt.savefig(os.path.join(output_dir, 'avg_crystalbleu_per_commit.png'), format='png')

plt.show()
