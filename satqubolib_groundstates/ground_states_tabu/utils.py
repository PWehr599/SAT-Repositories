import random
import pandas as pd
import os

from ground_states_tabu.plot import *


def choose_random_ids(pattern_qubo_dict, num_samples):
    """
    unique combinations necessary? - static set?
    """
    random_ids = []
    for i in range(num_samples):
        ranges = [
            range(0, len(pattern_qubo_dict[0]) - 1),
            range(0, len(pattern_qubo_dict[1]) - 1),
            range(0, len(pattern_qubo_dict[2]) - 1),
            range(0, len(pattern_qubo_dict[3]) - 1)
        ]

        random_ids.append([random.choice(rng) for rng in ranges])

    return random_ids


def fetch_identifiers_qubos(identifier_list, pattern_qubos_data, QUBO=True):
    result_list = []

    for type_index, identifier in enumerate(identifier_list):

        element = next((obj for obj in pattern_qubos_data[type_index] if obj.identifier == identifier), None)
        if element:
            result_list.append(element)

    return result_list


# Pandas Operations
def create_tabu_pandas_table():
    empty_table = pd.DataFrame()
    start_type = 0
    end_type = 3

    patterns = [f'Type_{i}_Qubo_Id' for i in range(start_type, end_type + 1)]

    # columns_to_keep = [col for col in data_frame.columns if col not in patterns]
    for column in patterns:
        # print(column)
        empty_table[column] = []
        # myTable.add_column(f'Type_{str(unique_type)}(#GS, #EL)', [])

    empty_table['Si_num_min_clauses_satisfied'] = []
    empty_table['Si_num_max_clauses_satisfied'] = []
    empty_table['Si_avg_clauses_satisified'] = []
    empty_table['Ground_State_Count'] = []
    print(empty_table)
    return empty_table


def fill_tabu_pandas_table(results, all_ground_states, empty_table: pd.DataFrame):
    # unfortunatly very slow to do it otherwise
    dictionary_list = []
    column_names = empty_table.columns

    for row_input in results:

        dictionary_data = \
            {
                column_names[0]: row_input[0],  # Type 0 Id
                column_names[1]: row_input[1],  # Type 1 Id
                column_names[2]: row_input[2],  # Type 2 Id
                column_names[3]: row_input[3],  # Type 3 Id
                column_names[4]: row_input[4],  # Si_num_min_clauses_satisfied,
                column_names[5]: row_input[5],  # Si_num_max_clauses_satisfied,
                column_names[6]: row_input[6]  # Si_avg_clauses_satisified
            }
        dictionary_list.append(dictionary_data)

    pandas_table = pd.DataFrame.from_dict(dictionary_list)
    pandas_table['Ground_State_Count'] = all_ground_states
    return pandas_table


def save_tabu_pandas_table(result_table, output_dir):
    output_path = os.path.join(output_dir, 'results')
    # print(output_path)
    # print(output_path)
    result_table.to_csv(output_path, index=False)


def plot_and_save(result_table, formula_name):
    output_dir = os.path.join(os.getcwd(), f"{formula_name}_Tabu_Results")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_tabu_pandas_table(result_table, output_dir)

    plot_data(result_table, output_dir)
