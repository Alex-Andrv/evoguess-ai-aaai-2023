import sys

from examples.get_hard_tasks import get_hard_tasks
from examples.heuristic_logic_minimizer.espresso_minimizer import get_simple_task_and_minimize
from examples.util.DIMACS_parser import parse_cnf
from examples.util.DIMACS_writer import print_clause
from instance.module.encoding import CNF
from typings.work_path import WorkPath


def print_usage():
    print("Use: python get_aaai_2023_task.py [backdoor_dir] [problem_with_learnt] [original_problem] <only-unit-clauses> ")

if __name__ == '__main__':
    if len(sys.argv) != 4 and len(sys.argv) != 5:
        print_usage()
        exit(0)
    backdoor_dir = sys.argv[1]
    problem_with_learnt = sys.argv[2]
    original_problem = sys.argv[3]
    out_problem_name = original_problem[:-4] + "_aaai_2023.cnf"
    only_unit_clauses = len(sys.argv) == 5

    root_path = WorkPath('examples')
    data_path = root_path.to_path('data')
    cnf_file = data_path.to_file(problem_with_learnt)
    logs_path = root_path.to_path('logs', 'aaai-2023')

    all_hard_tasks = get_hard_tasks(backdoor_dir, CNF(from_file=cnf_file), logs_path)
    new_clauses = []
    for hard_task in all_hard_tasks:
        if len(hard_task) > 500:
            print("skipp")
            continue

        mini_clauses = get_simple_task_and_minimize(hard_task)

        new_clauses += mini_clauses

    out = open(out_problem_name, 'w')
    clauses, var, clause_size = parse_cnf(open(original_problem, 'r'))
    out.write(f"p {var} {clause_size + len(new_clauses)} \n")

    for clause in clauses:
        print_clause(clause)

    for clause in new_clauses:
        if only_unit_clauses:
            if len(clause) == 1:
                print_clause(clause)
        else:
            print_clause(clause)