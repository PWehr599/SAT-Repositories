
from dimod.binary_quadratic_model import BinaryQuadraticModel

from ground_states_tabu.ground_states_calculations import *
from ground_states_tabu.utils import *
from ground_states_tabu.processing import *
from ground_states_tabu.assignments import *
from ground_states_tabu.tabu_processing import *

from satqubolib.formula import CNF
from satqubolib.transformations import PatternQUBONMSAT


class TabuGroundStatesGenerator:
    def __init__(self, formula_path, pattern_qubo_dict, use_random_pattern_choices, num_random_patterns=10,
                 pattern_qubo_ids=None, num_reads=10, time_out=50,
                 mini_sat_path='ground_states_tabu/compiled_minisat/bc_minisat_all_static_linux', mini_sat_timeout=120):
                # satqubolib_groundstates/ground_states_tabu/compiled_minisat/bc_minisat_all_release
        self.formula_path = formula_path
        self.cnf = CNF.from_file(formula_path)
        self.pattern_qubo_dict = pattern_qubo_dict
        self.use_random_pattern_choices = use_random_pattern_choices
        self.num_random_patterns = num_random_patterns
        self.pattern_qubo_ids = pattern_qubo_ids

        # Tabu Parameters
        self.num_reads = num_reads
        self.time_out = time_out

        # Minisat
        self.mini_sat_path = mini_sat_path
        self.mini_sat_timeout = mini_sat_timeout

    def generate_random_pattern_qubo_input(self):
        random_ids = choose_random_ids(self.pattern_qubo_dict, self.num_random_patterns)
        self.pattern_qubo_ids = random_ids

    def generate_formula_solution(self):
        sol_path = f'sol_{os.path.splitext(os.path.basename(self.formula_path))[0]}'
        run_all_sat(self.mini_sat_path, self.formula_path, sol_path, self.mini_sat_timeout)
        sol_lines = read_minisat_solutions(sol_path)
        binary_formula_solutions = convert_solver_inputs_concurrent(sol_lines)
        return binary_formula_solutions

    def count_ground_states(self):
        pattern_qubos_data = calculate_all_pattern_assignments(self.pattern_qubo_dict)
        if self.use_random_pattern_choices:
            self.generate_random_pattern_qubo_input()

        binary_formula_solutions = self.generate_formula_solution()
        pattern_qubo_inputs = []
        all_ground_states = []

        for pattern_qubo_id in self.pattern_qubo_ids:
            pattern_qubo_input = fetch_identifiers_qubos(pattern_qubo_id, pattern_qubos_data)

            total_groundstate_count = count_ground_states_concurrent(pattern_qubo_input, self.cnf.clauses,
                                                                     binary_formula_solutions)
            pattern_qubo_inputs.append(pattern_qubo_input)
            all_ground_states.append(total_groundstate_count)
        return pattern_qubo_inputs, all_ground_states

    def tabu_search(self, pattern_qubo_inputs):
        results = []
        for pattern_qubo_input in pattern_qubo_inputs:
            sat_qubo = PatternQUBONMSAT(self.cnf)

            sat_qubo.add_clause_qubos(pattern_qubo_input[0].qubo, pattern_qubo_input[1].qubo,
                                      pattern_qubo_input[2].qubo,
                                      pattern_qubo_input[3].qubo)
            sat_qubo.create_qubo()
            bqm = BinaryQuadraticModel.from_qubo(sat_qubo.qubo)
            output_vectors = sampler_tabu(bqm, self.num_reads, self.time_out)

            num_min_clauses_satisfied, num_max_clauses_satisfied, avg_clauses_satisified = satisfied_clauses_for_outputvectors(
                self.cnf.clauses, output_vectors)

            results.append(
                (pattern_qubo_input[0].identifier, pattern_qubo_input[1].identifier, pattern_qubo_input[2].identifier,
                 pattern_qubo_input[3].identifier, num_min_clauses_satisfied,
                 num_max_clauses_satisfied, avg_clauses_satisified))

        return results

    def count_gs_tabu_search_and_plot(self):
        pattern_qubo_inputs, all_ground_states = self.count_ground_states()

        results = self.tabu_search(pattern_qubo_inputs)

        df_tabu = create_tabu_pandas_table()

        result_table = fill_tabu_pandas_table(results, all_ground_states, df_tabu)

        plot_and_save(result_table, os.path.splitext(os.path.basename(self.formula_path))[0])
