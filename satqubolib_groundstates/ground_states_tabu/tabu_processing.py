from statistics import mean


def satisfied_clauses_for_outputvectors(formula, output_vectors):
    # TODO: just use min max
    collection_clauses_satisfied = []
    first_output_vector = output_vectors[0]
    output_vectors = output_vectors[1:]

    first_satisfied_clauses, _ = count_satisfied_clauses(formula, first_output_vector)
    num_min_clauses_satisfied = first_satisfied_clauses
    num_max_clauses_satisfied = first_satisfied_clauses
    collection_clauses_satisfied.append(first_satisfied_clauses)

    for output_vector in output_vectors:
        satisfied_clauses, _ = count_satisfied_clauses(formula, output_vector)
        if satisfied_clauses > num_max_clauses_satisfied:
            num_max_clauses_satisfied = satisfied_clauses
        if satisfied_clauses < num_min_clauses_satisfied:
            num_min_clauses_satisfied = satisfied_clauses
        collection_clauses_satisfied.append(satisfied_clauses)

    return num_min_clauses_satisfied, num_max_clauses_satisfied, mean(collection_clauses_satisfied)


def count_satisfied_clauses(formula, assignment):
    satisfied_clauses = 0
    unsat_clauses = []
    for clause in formula:
        clause_sat = False
        for literal in clause:
            if literal < 0 and assignment[abs(literal) - 1] == 0:
                satisfied_clauses += 1
                clause_sat = True
                break
            elif literal > 0 and assignment[abs(literal) - 1] == 1:
                satisfied_clauses += 1
                clause_sat = True
                break
        if not clause_sat:
            unsat_clauses.append(clause)
    return satisfied_clauses, unsat_clauses
