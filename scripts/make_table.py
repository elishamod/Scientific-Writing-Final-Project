import pandas as pd
import numpy as np
import os
import glob

# === CONFIG ===
path_pattern = "ztest/ztest_*.csv"  # Adjust path if needed
output_tex_file = "ztest/colored_factor_increase_table.tex"
output_csv_file = "ztest/combined_ztest.csv"
min_shading_value = 0.6
max_shading_value = 6

# === Category order ===
categories_in_order = ["astro-ph.CO", "astro-ph.EP", "astro-ph.GA", "astro-ph.HE",
                       "astro-ph.IM", "astro-ph.SR", "astro-ph",
                       "cond-mat", "hep", "nucl", "cs"]


# === Step 1: Load all CSVs and extract factor increases ===
all_results = {}

# for filepath in glob.glob(path_pattern):
#     category = os.path.basename(filepath).removeprefix("ztest_").removesuffix(".csv")
for category in categories_in_order:
    filepath = path_pattern.replace("*", category)
    df = pd.read_csv(filepath)

    # Keep only statistically significant results
    df = df[df["Significant (p<0.05)"] == "✓"].copy()

    # Compute factor increase
    def factor(row):
        if row["Before %"] > 0:
            return round(row["After %"] / row["Before %"], 2) 
        elif row["After %"] > 0:
            return -1
        else:
            return None

    df["Factor Increase"] = df.apply(factor, axis=1)

    all_results[category] = df.set_index("Word")["Factor Increase"]

# Combine into a full table
combined_df = pd.DataFrame(all_results).sort_index()
combined_df = combined_df.dropna(how="all")  # Drop words with no sig increase anywhere
# Save combined CSV
combined_df.to_csv(output_csv_file)
print(f"Combined CSV written to: {output_csv_file}")

# === Step 2: Apply LaTeX cell coloring ===
def color_cell(val, min_val=min_shading_value, max_val=max_shading_value,
               positive_color="green", negative_color="red"):
    """Return LaTeX code with color shading based on value (capped)."""
    if pd.isna(val):
        return ""
    if val == -1:
        return r"\cellcolor{%s!100} $\infty$" % positive_color
    if val == 1.0:
        return r"%.2f" % val
    elif val > 1.0:
        color = positive_color
        logval = np.log(min(val, max_val)) / np.log(max_val)
    else:
        color = negative_color
        logval = np.log(max(val, min_val)) / np.log(min_val)
    shade = int(logval * 100)
    return r"\cellcolor{%s!%d} %.2f" % (color, shade, val)

colored_df = combined_df.applymap(color_cell)

# === Step 3: Export to LaTeX ===
with open(output_tex_file, "w") as f:
    latex_table = colored_df.to_latex(
        na_rep="",
        escape=False,  # allow LaTeX commands like \cellcolor
        column_format="|l|" + "c|" * len(colored_df.columns),
        multicolumn=False,
        multicolumn_format="c"
    )
    f.write(latex_table)

print(f"LaTeX table written to: {output_tex_file}")

