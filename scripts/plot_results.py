import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

# Settings
CHATGPT_QUARTER = "2023-Q1"
# CATEGORIES = ["astro-ph.CO", "astro-ph.EP", "astro-ph.GA", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR"]
CATEGORIES = ["astro-ph", "cond-mat", "hep", "nucl", "cs"]


def main():
    df = load_csv()
    plot_usage(df)


def load_csv(filename="database/data_astro-ph.csv"):
    df = pd.read_csv(filename)
    return df


def plot_usage(df):
    TARGET_WORDS = df["Word"].unique()
    num_words = len(TARGET_WORDS)

    cols = 3  # number of columns in the subplot grid
    max_words_per_fig = 9

    split_word_lists = []
    figs, axeses = [], []
    k = 0
    while k < num_words:
        split_word_lists.append(TARGET_WORDS[k:min(k + max_words_per_fig, num_words + 1)])
        k += max_words_per_fig
        rows = (len(split_word_lists[-1]) + cols - 1) // cols  # compute rows needed
        fig, axes = plt.subplots(rows, cols, figsize=(15, 3 * rows), sharex=True)
        axes = axes.flatten()
        figs.append(fig)
        axeses.append(axes)

    for fignum, curr_word_list in enumerate(split_word_lists):
        for i, word in enumerate(curr_word_list):
            ax = axeses[fignum][i]
            subset = df[df["Word"] == word]
            x, y = subset["Quarter"], subset["Ratio of Abstracts"]
            ax.plot(x, y, marker='o', color='tab:blue')
            ax.set_title(f"'{word}' Usage Over Time")
            ax.set_ylabel("% of Abstracts")
            ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
            ax.set_xlabel("Quarter")
            ax.tick_params(axis='x', rotation=70)
            ax.grid(True)
            labels = subset["Quarter"].values
            if CHATGPT_QUARTER in labels:
                chatgpt_index = list(labels).index(CHATGPT_QUARTER)
                ax.axvline(chatgpt_index, color='red', linestyle='-', linewidth=1.5)
                # plot bars for before/after chatgpt
                before_bar_width = chatgpt_index
                rate_before = y[:chatgpt_index].sum() / before_bar_width
                ax.bar(before_bar_width / 2, rate_before, width=before_bar_width, align="center",
                       color="gray", alpha=0.3, label="Before avg")
                after_bar_width = len(list(labels)) - chatgpt_index
                rate_after = y[chatgpt_index:].sum() / after_bar_width
                ax.bar(chatgpt_index + after_bar_width / 2, rate_after, width=after_bar_width, align="center",
                       color="gray", alpha=0.3, label="After avg")
            # calculate and plot 3-quarters-averaged values
            avg_y = (y[:-2].values + y[1:-1].values + y[2:].values) / 3
            avg_x = x[1:-1]
            ax.plot(avg_x, avg_y, marker='o', color='tab:orange')
            ax.set_ylim(0, 1.02 * max(y.values))
        # Hide any extra axes
        for j in range(i + 1, len(axeses[fignum])):
            figs[fignum].delaxes(axeses[fignum][j])

        figs[fignum].tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

