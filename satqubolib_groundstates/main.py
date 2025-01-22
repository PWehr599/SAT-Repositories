from satqubolib.transformations import PatternQUBOFinder,ChancellorSAT
from tqdm import tqdm
from ground_states_tabu.generate_tabu_groundstates import *

if __name__ == '__main__':

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
        formula_path = 'test.cnf'
        pqf = PatternQUBOFinder(20)
        pattern_qubos = pqf.load("pattern_qubos/pattern_qubos_2_2.pkl")
        gs_obj = TabuGroundStatesGenerator(formula_path, pattern_qubos, True)
        gs_obj.count_gs_tabu_search_and_plot()

