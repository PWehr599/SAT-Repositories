import itertools
import pandas as pd
import tqdm
import concurrent.futures
import math
import tqdm.autonotebook as tqdman
import multiprocessing


# ------------------------------------------------------------------------------------------------------------------
# Ground State Counter for Superimposed QUBO given a formula with parallel computing

def count_ground_states(pattern_qubo_input, formula, solutions):
    """
    Non concurrent version of ground_state counter
    pattern_qubo_input: list of qubo inputs for which we want to count the ground states given the formula
    formula: formula input
    solutions: formula solutions in binary format

    returns: total_ground_states: total number of ground states for given formula and pattern qubo configuration
    """
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
    """
    pattern_qubo_input: list of qubo inputs for which we want to count the ground states given the formula
    formula: formula input
    solutions_chunk: formula solution chunk in binary format

    returns: total_ground_states: total number of ground states for given formula and pattern qubo configuration
    """
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
    """
    Concurrent version of count_ground_states function
    Splits the solutions into chunks given the number of available cores
    Since the input chunks do not depend on each other this is threadsafe
    With - concurrent.futures.as_completed only completed groundstate chunk calculations are added up one by one
    (Threads handled by python natively)

    pattern_qubo_input: list of qubo inputs for which we want to count the ground states given the formula
    formula: formula input
    solutions: formula solutions in binary format

    returns: total_ground_states: total number of ground states for given formula and pattern qubo configuration
    """
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
# Brute Force SAT Formula solver - applicable for very small SAT formulas (> 150 Clauses)

def is_satisfiable(formula, assignment):
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
        assignment = [bool(int(bit)) for bit in input_combination]

        if is_satisfiable(formula, assignment):
            solutions.append(input_combination)

    return solutions


def generate_binary_inputs(num_variables):
    return [format(i, '0' + str(num_variables) + 'b') for i in range(2 ** num_variables)]


# ------------------------------------------------------------------------------------------------------------------
# Helper functions for converting output from ALLSAT solver and sorting formulas

def convert_solver_input(solution):
    """
    Binary Solution needed for ground State Calculations
    solution: Minisat outputs of form (1 -2 -3 -4 -5 6 -7 -8 -9 10 11 -12 -13 14 -15 16 ...) for n variables for a Formula
    Converts the string from the solution file line by line to binary: if -x => 0 , otherwise 1
    Here: (1 -2 -3 -4 -5 6 -7 -8 -9 10 11 -12 -13 14 -15 16 ...) => (1 0 0 0 0 1 0 0 0 1 1 0 0 1 0 1 ...)
    (Probably distinction of negation and non negation possible as well instead of 0/1)
    """
    binary_solution = ''.join('1' if num[0] != '-' else '0' for num in solution.split()[:-1])
    return binary_solution


def convert_solver_inputs_concurrent(solutions):
    """
    Concurrent Approach for large Formula solution files
    Split solution space into chunks for binary conversion with pool.map
    """
    pool = multiprocessing.Pool()
    binary_list = pool.map(convert_solver_input, solutions)
    pool.close()
    pool.join()
    return binary_list


def sort_formula(formula):
    """
    Sort formulas in order of the Type Clauses (negations at the end like in Pattern Qubo Paper)
    (This is now done in satqubolib automatically)
    """
    formula = [sorted(clause, reverse=True) for clause in formula]
    return formula
