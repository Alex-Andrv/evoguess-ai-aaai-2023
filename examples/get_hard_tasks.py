# function submodule imports
import os

from function.module.solver import pysat
from function.module.measure import SolvingTime

# instance module imports
from instance.impl import Instance
from instance.module.encoding import CNF
from instance.module.variables import Indexes, make_backdoor

# other imports
from core.impl import Combine
from output.impl import OptimizeLogger
from executor.impl import ProcessExecutor

def get_hard_tasks(backdoor_dir: str, cnf_file: CNF, logs_path):
    directory = 'examples'

    all_hard_tasks = []

    for filename in os.listdir(os.path.join(directory, backdoor_dir)):
        input = open(os.path.join(directory, backdoor_dir, filename), 'r')
        str_backdoors = [input.readline().strip()]
        input.close()
        backdoors = [
            make_backdoor(Indexes(from_string=str_vars))
            for str_vars in str_backdoors
        ]
        print(filename)

        combine = Combine(
            instance=Instance(
                encoding=cnf_file
            ),
            measure=SolvingTime(),
            solver=pysat.Glucose3(),
            logger=OptimizeLogger(logs_path),
            executor=ProcessExecutor(max_workers=4),
            filename=os.path.join(backdoor_dir, filename)
        )

        estimation = combine.launch(*backdoors, return_hard_task=True)
        all_hard_tasks.append(estimation['acc_hard_tasks'])
        cnt_hard_tasks = estimation['hard_tasks']
        total_tasks = estimation['total_tasks']
        print(f'backdoor {backdoors[0]} produce {cnt_hard_tasks} hard tasks. Total tasks {total_tasks}')
    return all_hard_tasks

