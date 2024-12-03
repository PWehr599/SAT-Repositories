import pandas as pd
import matplotlib.pyplot as plt


def plot_data(df, save_dir):
    #
    df['Ground_State_Count'] = df['Ground_State_Count'].astype(float)
    df_sorted = df.sort_values(by='Ground_State_Count')
    attributes = ['Si_num_min_clauses_satisfied', 'Si_num_max_clauses_satisfied', 'Si_avg_clauses_satisified']

    for attribute in attributes:
        ax = df_sorted.plot(x='Ground_State_Count', y=attribute, kind='line', marker='o')

        ax.set_xscale('log')
        plt.title(f"{attribute} vs Ground_State_Count")
        plt.xlabel("Ground_State_Count")
        plt.ylabel(attribute)
        plt.grid()
        plt.savefig(f"{save_dir}/{attribute}.png")
