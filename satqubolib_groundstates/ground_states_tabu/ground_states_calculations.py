import itertools
import pandas as pd
import tqdm
import concurrent.futures
import math
import tqdm.autonotebook as tqdman
import multiprocessing


# ------------------------------------------------------------------------------------------------------------------

def count_ground_states(pattern_qubo_input, formula, solutions):
    formula = sort_formula(formula)
    total_groundstate_count = 0  # 1 threadsafe
    clause_types = [sum(1 for num in clause if num < 0) for clause in formula]

    for solution in solutions:
        assignment_ground_state_count = 1

        for index, clause in enumerate(formula):
            clause_assignment = ''
            clause_assignment += str(solution[abs(clause[0]) - 1])
            clause_assignment += str(solution[abs(clause[1]) - 1])
            clause_assignment += str(solution[abs(clause[2]) - 1])

            assignment_ground_state_count *= pattern_qubo_input[clause_types[index]].ground_state_assignments[
                clause_assignment]

        total_groundstate_count += assignment_ground_state_count

    return total_groundstate_count


def count_ground_states_worker(pattern_qubo_input, formula, clause_types, solutions_chunk):
    total_groundstate_count = 0

    for solution in solutions_chunk:
        assignment_ground_state_count = 1

        for index, clause in enumerate(formula):
            clause_assignment = ''
            clause_assignment += str(solution[abs(clause[0]) - 1])
            clause_assignment += str(solution[abs(clause[1]) - 1])
            clause_assignment += str(solution[abs(clause[2]) - 1])

            assignment_ground_state_count *= pattern_qubo_input[clause_types[index]].ground_state_assignments[
                clause_assignment]

        total_groundstate_count += assignment_ground_state_count

    return total_groundstate_count


def count_ground_states_concurrent(pattern_qubo_input, formula, solutions):
    num_processes = multiprocessing.cpu_count()
    formula = sort_formula(formula)
    clause_types = [sum(1 for num in clause if num < 0) for clause in formula]
    chunk_size = math.ceil(len(solutions) / num_processes)
    solution_chunks = [solutions[i:i + chunk_size] for i in range(0, len(solutions), chunk_size)]

    total_groundstate_count = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [executor.submit(count_ground_states_worker, pattern_qubo_input, formula, clause_types, chunk) for
                   chunk in solution_chunks]

        for future in concurrent.futures.as_completed(futures):  # threadsafe w/ as_completed
            total_groundstate_count += future.result()

    return total_groundstate_count


# ------------------------------------------------------------------------------------------------------------------
def is_satisfiable(formula, assignment):
    # print(assignment)
    # print("----------")
    for clause in formula:
        clause_satisfied = False
        for literal in clause:
            variable = abs(literal)
            if (literal > 0 and assignment[variable - 1]) or (literal < 0 and not assignment[variable - 1]):
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False
    return True


def calculate_solutions(args):
    formula, binary_inputs = args
    solutions = []
    for input_combination in binary_inputs:
        # print(input_combination)
        assignment = [bool(int(bit)) for bit in input_combination]
        # print(assignment)

        if is_satisfiable(formula, assignment):
            solutions.append(input_combination)

    return solutions


def generate_binary_inputs(num_variables):
    return [format(i, '0' + str(num_variables) + 'b') for i in range(2 ** num_variables)]


# ------------------------------------------------------------------------------------------------------------------

def convert_solver_input(solution):
    binary_solution = ''.join('1' if num[0] != '-' else '0' for num in solution.split()[:-1])
    return binary_solution


def convert_solver_inputs_concurrent(solutions):
    pool = multiprocessing.Pool()
    binary_list = pool.map(convert_solver_input, solutions)
    pool.close()
    pool.join()
    return binary_list


def sort_formula(formula):
    formula = [sorted(clause, reverse=True) for clause in formula]
    return formula
