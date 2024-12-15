import subprocess
import os
import dimod as di
from tabu import TabuSampler


def run_all_sat(mini_sat_path, input_file_path, output_file_path, timeout=120):
    """
    mini_sat_path: compiled minisat solver
    input_file_path: formula to be solved
    output_file_path: text file containing all solutions
    timeout: maximal allocated time for minisat solver to generate all solutions
    (If timeout smaller than actual solution time required sol file will be incomplete)
    """

    if not os.path.isfile(mini_sat_path):
        print(f"File not found: {mini_sat_path}")
        return False
    if not os.access(mini_sat_path, os.X_OK):
        print(f"File is not executable: {mini_sat_path}")
        return False

    try:
        result = subprocess.run(
            [f"./{mini_sat_path}", input_file_path, output_file_path],
            timeout=timeout,
            check=True
        )
        return True

    except subprocess.TimeoutExpired:
        print(f"The process timed out after {timeout} seconds.")
    except subprocess.CalledProcessError as e:
        print(f"The process failed with exit code {e.returncode}.")
    except OSError as e:
        print(f"OSError: {e}")

    return False


def read_minisat_solutions(sol_file_path):
    with open(sol_file_path) as file:
        lines = file.readlines()
    return lines


def sampler_tabu(qubo_as_bqm, num_reads: int, timeout: int):

    samples = TabuSampler().sample(qubo_as_bqm, num_reads=num_reads, timeout=timeout)
    output_vectors = samples.record.sample
    return output_vectors
