import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("../evaluation_results.csv")

sns.histplot(df['line_match_after_vs_chatgpt'], kde=True)
plt.title("Distribution of Similarity Score")
plt.xlabel("CrystalBLEU")
plt.ylabel("Frequency")
plt.show()
