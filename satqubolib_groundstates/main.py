from satqubolib.transformations import PatternQUBOFinder,ChancellorSAT
from tqdm import tqdm
from ground_states_tabu.generate_tabu_groundstates import *
def get_false_assignments(solutions):
    bitstring_length = len(solutions[0])

    all_possible_bitstrings = set(format(i, f'0{bitstring_length}b') for i in range(2 ** bitstring_length))

    given_bitstrings_set = set(solutions)

    missing_bitstrings = all_possible_bitstrings - given_bitstrings_set

    return missing_bitstrings
def count_distinct_vars(formula):
    unique_absolute_values = set()

    # Iterate over each sublist in the nested list
    for sublist in formula:
        for number in sublist:
            # Add the absolute value to the set
            unique_absolute_values.add(abs(number))

    # The number of distinct absolute values
    distinct_count = len(unique_absolute_values)
    return distinct_count

def flatten(xss):
    return [x for xs in xss for x in xs]


def energy_assignments(solutions, sampleset, interest_len):
    all_match_samples = []
    all_match_energies = []
    for solution in solutions:
        solution = [int(char) for char in solution]
        # print(solution)
        samples = sampleset.record.sample
        energies = sampleset.record.energy

        # Extract the variable names
        variable_labels = sampleset.variables

        # Define the variables of interest
        variables_of_interest = variable_labels[:interest_len]

        # Filter the samples based on the bitstring
        matching_samples = []
        matching_energies = []

        for sample, energy in zip(samples, energies):
            # Extract the values for the first 3 variables
            sample_values = [sample[i] for i in range(len(variables_of_interest))]

            if sample_values == solution:
                matching_samples.append(sample)
                matching_energies.append(energy)

        all_match_samples.append(matching_samples)
        all_match_energies.append(matching_energies)

    return all_match_samples, all_match_energies


def min_energy_assigments(solution, sampleset, interest_len):
    solution = [int(char) for char in solution]
    samples = sampleset.record.sample
    energies = sampleset.record.energy
    min_energy = float('inf')  # Start with infinity, so any actual energy will be lower
    min_sample = None

    for sample, energy in zip(samples, energies):
        # Extract the values for the first 3 variables
        sample_values = [sample[i] for i in range(interest_len)]

        # Check if the sample matches the desired bitstring
        if sample_values == solution:
            # If the current energy is lower than the minimal energy found so far
            if energy < min_energy:
                # Update the minimal energy and corresponding sample
                min_energy = energy
                min_sample = sample
    return min_sample, min_energy
def convert_solver_inputs_baseline(solutions):
    # WORKING
    binary_list = []
    for solution in solutions:
        binary_solution = ''.join(map(lambda num: '1' if num[0] != '-' else '0', solution.split()[:-1]))
        binary_list.append(binary_solution)
    return binary_list
def save_formula_to_dimacs(formula, filename):
    """
    Saves a given 3-SAT formula to a .dimacs file.

    :param formula: List of lists, where each inner list is a clause represented by integers.
    :param filename: Name of the file to save the formula.
    """
    # Calculate the number of variables
    num_vars = max(abs(literal) for clause in formula for literal in clause)
    num_clauses = len(formula)

    with open(filename, 'w') as f:
        # Write the header
        f.write(f"p cnf {num_vars} {num_clauses}\n")

        # Write each clause
        for clause in formula:
            f.write(" ".join(map(str, clause)) + " 0\n")
if __name__ == '__main__':
    def example():
        pqf = PatternQUBOFinder(20)

        formula_path = 'dataset/no_triangle/800/0.cnf'

        pattern_qubos = pqf.load("pattern_qubos.pkl")
        cnf = CNF([[1, 2, 3], [-1, -4, -5]])  # The CNF formula is (x1 v x2 v x3) and (x1 v x2 v -x3)
        # sat_qubo = ChoiSAT(cnf)
        sat_qubo = ChancellorSAT(cnf)
        # sat_qubo = NuessleinNMSAT(cnf)
        # sat_qubo = Nuesslein2NMSAT(cnf)

        sat_qubo.create_qubo()
        sat_qubo.print_qubo()
        bqm = BinaryQuadraticModel.from_qubo(sat_qubo.qubo)
        sampleset = di.ExactSolver().sample(bqm)
        print(sampleset)
        mini_sat_path = 'ground_states_tabu/compiled_minisat/bc_minisat_all_release'
        file_path = 'formula.dimacs'
        output_file_path = 'sol.txt'
        save_formula_to_dimacs(cnf.clauses, file_path)
        run_all_sat(mini_sat_path,file_path, output_file_path)
        with open(output_file_path,
                  'r') as file:
            lines = file.readlines()
        # Extract the samples and corresponding energies

        solutions = convert_solver_inputs_baseline(lines)

        # print(solutions)
        false_assigmnents = get_false_assignments(solutions)

        # find all ancilla samples
        # all_match_samples, all_match_energies = energy_assignments(solutions, sampleset, interest_len)
        # for all_match_sample, all_match_energy in zip(all_match_samples, all_match_energies):
        #    print(all_match_sample, all_match_energy)
        #    print("##########################")
        print(solutions)
        num_vars = count_distinct_vars(cnf.clauses)
        all_min_samples_sol = []
        all_min_energies_sol = []
        all_min_samples_false = []
        all_min_energies_false = []
        interest_len = num_vars
        for solution in tqdm.tqdm(solutions, desc='sol_calc', total=len(solutions)):
            # def min_energy_assigments(solution, sampleset, interest_len):
            min_sample, min_energy = min_energy_assigments(solution, sampleset, interest_len)
            # print(min_sample, min_energy)
            all_min_samples_sol.append(min_sample)
            all_min_energies_sol.append(min_energy)
        print(min(all_min_energies_sol))
        print(max(all_min_energies_sol))
        print('false_assigmnents')

        for false_assigmnent in tqdm.tqdm(false_assigmnents, desc='false_calc', total=len(false_assigmnents)):
            min_sample, min_energy = min_energy_assigments(false_assigmnent, sampleset, interest_len)
            # print(min_sample, min_energy)
            all_min_samples_false.append(min_sample)
            all_min_energies_false.append(min_energy)
        print(min(all_min_energies_false))
        print(max(all_min_energies_false))
        print("######NEW_FORMULA#######")
        """
        TabuGroundStatesGenerator Inputs:
        
        formula_path: formula path for formula to solve
        pattern_qubo_dict: Pattern Qubos use for superimposing
        use_random_pattern_choices: generate random Pattern Qubo combinations
        num_random_patterns: how many combinations from random to be evaluated

        pattern_qubo_ids: set the ids yourself in List form [[1,2,3,4],[4,5,3,2]]
        where each sublist corresponds to: [Type_0_Id, Type_1_Id, Type_2_Id, Type_3_Id]
        
        num_reads,time_out: Tabu Sampler Settings
        
        mini_sat_path: Path for compiled Minisat object to generate all formula solutions
        mini_sat_timeout: seconds for finding a solution before timeout
        (with large formulas the resulting sol.txt can get very large, make sure there is enough disk space)
        """

        #gs_obj = TabuGroundStatesGenerator(formula_path, pattern_qubos, True)
        #gs_obj.count_gs_tabu_search_and_plot()

    example()
