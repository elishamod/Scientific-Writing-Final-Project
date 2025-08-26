import pandas as pd
import os
import glob

# === CONFIG ===
path_pattern = "ztest/ztest_*.csv"  # Adjust path if needed
output_tex_file = "ztest/colored_factor_increase_table.tex"
max_shading_value = 5  # Anything >= this will get full blue (blue!100)

# === Step 1: Load all CSVs and extract factor increases ===
all_results = {}

for filepath in glob.glob(path_pattern):
    category = os.path.basename(filepath).removeprefix("ztest_").removesuffix(".csv")
    df = pd.read_csv(filepath)

    # Keep only statistically significant results
    df = df[df["Significant (p<0.05)"] == "✓"].copy()

    # Compute factor increase
    df["Factor Increase"] = df.apply(
        lambda row: round(row["After %"] / row["Before %"], 2) if row["Before %"] > 0 else None,
        axis=1
    )

    all_results[category] = df.set_index("Word")["Factor Increase"]

# Combine into a full table
combined_df = pd.DataFrame(all_results).sort_index()
combined_df = combined_df.dropna(how="all")  # Drop words with no sig increase anywhere

# === Step 2: Apply LaTeX cell coloring ===
def color_cell(val, max_val=max_shading_value):
    """Return LaTeX code with blue shading based on value (capped)."""
    if pd.isna(val):
        return ""
    shade = int(min(val, max_val) / max_val * 100)
    return r"\cellcolor{blue!%d} %.2f" % (shade, val)

colored_df = combined_df.applymap(color_cell)

# === Step 3: Export to LaTeX ===
with open(output_tex_file, "w") as f:
    latex_table = colored_df.to_latex(
        na_rep="",
        escape=False,  # allow LaTeX commands like \cellcolor
        column_format="l" + "r" * len(colored_df.columns),
        multicolumn=False,
        multicolumn_format="c"
    )
    f.write(latex_table)

print(f"LaTeX table written to: {output_tex_file}")

