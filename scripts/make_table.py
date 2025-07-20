import pandas as pd
import os
import glob

path_pattern = "ztest/ztest_*.csv"  # adjust if needed
all_results = {}

for filepath in glob.glob(path_pattern):
    category = os.path.basename(filepath).removeprefix("ztest_").removesuffix(".csv")
    df = pd.read_csv(filepath)
    df = df[df["Significant (p<0.05)"] == "✓"].copy()

    df["Factor Increase"] = df.apply(
        lambda row: round(row["After %"] / row["Before %"], 2) if row["Before %"] > 0 else None,
        axis=1
    )

    all_results[category] = df.set_index("Word")["Factor Increase"]

# Combine all into one table
combined_df = pd.DataFrame(all_results).sort_index()
combined_df = combined_df.dropna(how="all")

# Save as CSV and LaTeX
combined_df.to_csv("ztest/combined_factor_increase.csv")
combined_df.to_latex("ztest/combined_factor_increase.tex", na_rep="", float_format="%.2f")

