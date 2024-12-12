from xmlrpc.client import Boolean

from satqubolib.transformations import PatternQUBOFinder,ChancellorSAT
from tqdm import tqdm
from ground_states_tabu.generate_tabu_groundstates import *
import argparse

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

        parser = argparse.ArgumentParser(description="Example Python program with arguments.")
        parser.add_argument("--formula_path", required=True, help="formula path")
        parser.add_argument("--use_random", required=True, type=bool,help="Random QUBO choice")
        parser.add_argument("--num_random", required=True, type=int,help="Number of random QUBOs")
        parser.add_argument("--num_reads", required=True, type=int,help="TABU number of reads")
        parser.add_argument("--timeout_TABU", required=True, type=int,help="TABU timeout")
        parser.add_argument("--timeout_minisat", required=True, type=int,help="Minisat timeout")

        # Optional argument for pattern_qubo_dict with a default value
        parser.add_argument(
                "--pattern_qubo_file",
                default="pattern_qubos/pattern_qubos.pkl",  # Default to this file
                help="Path to the Pattern QUBO file (Interval: -2,2, step size: 1) (default: 'pattern_qubos/pattern_qubos.pkl')",
        )

        args = parser.parse_args()

        pqf = PatternQUBOFinder(20)
        pattern_qubos = pqf.load(args.pattern_qubo_file)

        gs_obj = TabuGroundStatesGenerator(formula_path=args.formula_path, pattern_qubo_dict=pattern_qubos,
                                           use_random_pattern_choices=args.use_random, num_random_patterns=args.num_random,
                                           num_reads = args.num_reads, time_out=args.timeout_TABU,mini_sat_timeout=args.timeout_minisat)
        gs_obj.count_gs_tabu_search_and_plot()

'''
code path to mounted volume inside functions - /Users/philippewehr/Desktop/Test - this path for dir with the corresponding formula 
docker run 
  -v /Users/philippewehr/Desktop/Test:/satqubolib_groundstates/shared \  
  python-satqubolib \
  --formula_path="/satqubolib_groundstates/shared/10.cnf" \
  --use_random=True \
  --num_random=1 \
  --num_reads=1 \
  --timeout_TABU=1 \
  --timeout_minisat=300
docker run \
  -v /home/philippe-wehr/Schreibtisch:/satqubolib_groundstates/shared \  
  python-satqubolib \
  --formula_path="/satqubolib_groundstates/shared/10.cnf" \
  --use_random=True \
  --num_random=1 \
  --num_reads=1 \
  --timeout_TABU=1 \
  --timeout_minisat=300

'''