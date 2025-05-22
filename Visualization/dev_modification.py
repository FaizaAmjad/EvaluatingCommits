import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load your data
df = pd.read_csv('../evaluation_results.csv')

# Group by commit SHA and compute mean scores
grouped = df.groupby('sha')[['dev_used_as_is', 'dev_modified', 'dev_own_lines']].mean()

# Sort by total GPT reuse (used as is + modified)
grouped['total_gpt_reuse'] = grouped['dev_used_as_is'] + grouped['dev_modified']
grouped = grouped.sort_values('total_gpt_reuse', ascending=False)
grouped = grouped.drop(columns='total_gpt_reuse')

# Plot stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))

x = np.arange(len(grouped))
ax.bar(x, grouped['dev_used_as_is'], label='Exact GPT Reuse')
ax.bar(x, grouped['dev_modified'], bottom=grouped['dev_used_as_is'], label='Modified GPT')
bottoms = grouped['dev_used_as_is'] + grouped['dev_modified']
ax.bar(x, grouped['dev_own_lines'], bottom=bottoms, label='Developer Original')

ax.set_ylabel('Proportion of Added Lines')
ax.set_title('Developer Behavior Per Commit (Reused vs Original)')
ax.set_xticks(x)
ax.set_xticklabels([f'commit {i+1}' for i in range(len(grouped))], rotation=45)
ax.set_ylim(0, 1)
ax.legend()
ax.grid(True, axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.xticks([])  # hides x-tick labels
plt.xlabel('')  # removes x-axis label text

# Ensure 'images' folder exists
output_dir = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(output_dir, exist_ok=True)

# Save plot as PDF
output_path = os.path.join(output_dir, 'exact_modified_original.pdf')
plt.savefig(output_path, format='pdf')

#save plot as png
plt.savefig(os.path.join(output_dir, 'exact_modified_original.png'), format='png')

plt.show()
