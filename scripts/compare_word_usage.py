import pandas as pd
from statsmodels.stats.proportion import proportions_ztest
import os
from glob import glob

# settings
DATABASE_DIRC = "database"
OUTPUT_DIRC = "ztest"
CHATGPT_QUARTER = "2023-Q1"


def main():
    os.makedirs(OUTPUT_DIRC, exist_ok=True)
    data_files = glob(os.path.join(DATABASE_DIRC, "data_*.csv"))
    for data_file in data_files:
        filename = os.path.basename(data_file)
        category = filename[5:-4]
        output_file = os.path.join(OUTPUT_DIRC, f"ztest_{category}.csv")
        analyze_data(data_file, output_file)


def analyze_data(data_file, output_file):
    df = pd.read_csv(data_file)
    df["QuarterIndex"] = df["Quarter"].map(quarter_sort_key)
    cutoff_index = quarter_sort_key(CHATGPT_QUARTER)

    results = []
    for word in df["Word"].unique():
        word_df = df[df["Word"] == word]
        before = word_df[word_df["QuarterIndex"] < cutoff_index]
        after = word_df[word_df["QuarterIndex"] >= cutoff_index]

        a = before["Abstact Count"].sum()
        n1 = before["Total Abstracts Read"].sum()
        b = after["Abstact Count"].sum()
        n2 = after["Total Abstracts Read"].sum()

        if n1 > 0 and n2 > 0:
            count = [a, b]
            nobs = [n1, n2]
            z_stat, pval = proportions_ztest(count, nobs)
            p1 = a / n1
            p2 = b / n2

            results.append({
                "Word": word,
                "Before %": round(p1 * 100, 2),
                "After %": round(p2 * 100, 2),
                "Change in %": round((p2 - p1) * 100, 2),
                "z-stat": round(z_stat, 4),
                "p-value": f"{pval:.1e}",
                "Significant (p<0.05)": "✓" if pval < 0.05 else ""
            })
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("p-value")
    results_df.to_csv(output_file, index=False)
    print(f"Saved results to {output_file}")


def quarter_sort_key(q):
    """Convert 'YYYY-Qx' to sortable index like 2023-Q1 -> 8093"""
    year, qnum = q.split("-Q")
    return int(year) * 4 + int(qnum)


if __name__ == "__main__":
    main()

