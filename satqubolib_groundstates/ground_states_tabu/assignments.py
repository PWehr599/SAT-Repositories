from dataclasses import dataclass


@dataclass
class PatternQuboAssignments:
    qubo: dict
    ground_state_assignments: dict
    identifier: int
    type: int


def calculate_all_pattern_assignments(pattern_qubo_dict: dict):
    pattern_qubo_class_dict = {}
    for i in range(4):
        pattern_qubo_class_dict[i] = []

    for key in pattern_qubo_dict:
        identifier = 0
        for pattern_qubo in pattern_qubo_dict[key]:
            ground_state_assignments = ground_state_assigments(pattern_qubo, key)
            pattern_data_obj = PatternQuboAssignments(pattern_qubo, ground_state_assignments, identifier=identifier,
                                                      type=key)
            pattern_qubo_class_dict[key].append(pattern_data_obj)
            identifier += 1

    return pattern_qubo_class_dict


def ground_state_assigments(qubo, type):
    # TODO: Maybe iterate over len - 1 and add ancilla after

    num_variables = max(max(key) for key in qubo) + 1
    assignments = all_binary_strings(num_variables)

    ground_state_assignments = {}

    if type == 0:
        assignments.remove('0000')
        assignments.remove('0001')
    if type == 1:
        assignments.remove('0010')
        assignments.remove('0011')
    if type == 2:
        assignments.remove('0110')
        assignments.remove('0111')
    if type == 3:
        assignments.remove('1110')
        assignments.remove('1111')

    for i in range(0, len(assignments), 2):
        # Get two elements per iteration
        element_anc1 = assignments[i]
        element_anc2 = assignments[i + 1] if i + 1 < len(assignments) else None

        energy_anc1 = sum(
            qubo.get((i, j), 0) * int(element_anc1[i]) * int(element_anc1[j]) for i in range(num_variables) for j in
            range(num_variables))

        energy_anc2 = sum(
            qubo.get((i, j), 0) * int(element_anc2[i]) * int(element_anc2[j]) for i in range(num_variables) for j in
            range(num_variables))

        element_no_anc = element_anc1[:-1]

        if energy_anc1 == energy_anc2:
            ground_state_assignments[element_no_anc] = 2
        else:
            ground_state_assignments[element_no_anc] = 1

    return ground_state_assignments


def all_binary_strings(n):
    if n == 0:
        return ['']
    else:
        prev_strings = all_binary_strings(n - 1)
        return [string + bit for string in prev_strings for bit in ['0', '1']]
