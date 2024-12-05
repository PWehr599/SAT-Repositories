import pandas as pd
import matplotlib.pyplot as plt

def plot_data(df, save_dir):

    df['Ground_State_Count'] = df['Ground_State_Count'].astype(float)

    df_sorted = df.sort_values(by='Ground_State_Count')

    attributes = {
        'Si_num_min_clauses_satisfied': 'Number of minimal Clauses satisfied',
        'Si_num_max_clauses_satisfied': 'Number of maximal Clauses satisfied',
        'Si_avg_clauses_satisified': 'Average Clauses satisfied'
    }

    for attribute, label in attributes.items():
        ax = df_sorted.plot(x='Ground_State_Count', y=attribute, kind='scatter', marker='x')

        ax.set_xscale('log')

        plt.title(f"{label} vs Ground State Count")
        plt.xlabel("Ground State Count")
        plt.ylabel(label)

        plt.grid()

        plt.savefig(f"{save_dir}/{attribute}.png")

        plt.clf()
