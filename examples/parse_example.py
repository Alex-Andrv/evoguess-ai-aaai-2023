from output.impl import OptimizeParser
from typings.work_path import WorkPath

if __name__ == '__main__':
    root_path = WorkPath('examples')
    logs_path = root_path.to_path('logs', 'pancake_vs_selection_5_4')

    log_dir = '2023.07.07-02:34:15_?'
    log_path = logs_path.to_path(log_dir)

    with OptimizeParser(log_path) as parser:
        for iteration in parser.parse():
            best_point = sorted(iteration.points)[0]
            print(iteration.index, best_point)
