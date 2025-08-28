import pandas as pd

latex_table_path = "ztest/colored_factor_increase_table.tex"
save_path = "ztest/significant_words.txt"
major_categories = ["astro-ph", "cond-mat", "hep", "nucl", "cs"]
data = pd.read_csv("ztest/combined_ztest.csv", index_col=0)
data = data[major_categories]

data = data.fillna(1.0)
data = data.replace(-1, 100)

# find words that have values > 1.5 in at least 3 of the major categories
def is_significant(row):
    count = sum(row[cat] > 1.5 for cat in major_categories)
    return count >= 3
significant_words = data[data.apply(is_significant, axis=1)]
significant_words = significant_words.index.tolist()

f = open(latex_table_path, "r").read()
for word in significant_words:
    if "textbf{" + word + "}" not in f:
        f = f.replace(word, "\\textbf{" + word + "}")
open(latex_table_path, "w").write(f)

f = open(save_path, "w")
f.write("\n".join(significant_words))
f.close()
