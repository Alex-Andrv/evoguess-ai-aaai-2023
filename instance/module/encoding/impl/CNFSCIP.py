from threading import Lock
from typing import List, Tuple

from pyscipopt.scip import Model, PY_SCIP_PARAMSETTING

from .. import CNFData, CNF

Coef = int
Lit = int
Term = Tuple[Coef, Lit]
Clause = List[int]
Clauses = List[Clause]

pb_data = {}
parse_lock = Lock()
cnf_data = {}

class CNFSCIPData(CNFData):
    def __init__(self, clauses: Clauses, lines: str = None, max_lit: int = None):
        super().__init__(clauses, lines, max_lit)

        model = Model()

        assert max_lit != None

        for lit in range(1, max_lit + 1):
            model.addVar(vtype='B', name=str(lit))

        model.hideOutput()
        model.setParam('display/verblevel', 5)

        for clause in clauses:
            line = 0
            dl = 0
            for c in clause:
                var = model.getVars()[abs(c) - 1]
                assert var.name == str(abs(c))
                if c > 0:
                    line += 1 * var
                else:
                    line += -1 * var
                    dl += 1

            model.addCons(line >= 1 - dl)

        # model.setPresolve(PY_SCIP_PARAMSETTING.AGGRESSIVE)
        # model.presolve()
        # model.setPresolve(PY_SCIP_PARAMSETTING.DEFAULT)
        assert len(model.getVars()) == max_lit, "presolver shrink vars"
        self.model = model

    def get_model(self):
        return self.model


class CNFSCIP(CNF):
    slug = 'encoding:CNF:CNFSCIP'

    def __init__(self, from_clauses: Clauses = None, from_file: str = None):
        super().__init__(from_clauses, from_file)
        self.clauses = from_clauses

    def _parse_raw_data(self, raw_data: str):
        process_line = 1
        try:
            lines, clauses, max_lit = [], [], 0
            for line in raw_data.splitlines(keepends=True):
                if line[0] not in self.comment_lead:
                    clause = [int(n) for n in line.split()[:-1]]
                    max_lit = max(max_lit, *map(abs, clause))
                    clauses.append(clause)
                    lines.append(line)
                process_line += 1

            cnf_data[self.filepath] = CNFSCIPData(
                clauses, ''.join(lines), max_lit
            )
        except Exception as exc:
            msg = f'Error while parsing encoding file in line {process_line}'
            raise ValueError(msg) from exc

    def _process_raw_data(self):
        with parse_lock:
            if self.filepath in cnf_data:
                return

            data = self.get_raw_data()
            self._parse_raw_data(data)

    def get_data(self) -> CNFData:
        if self.clauses:
            return CNFData(self.clauses)
        elif self.filepath in cnf_data:
            return cnf_data[self.filepath]

        self._process_raw_data()
        return cnf_data[self.filepath]

    def __copy__(self):
        return CNFSCIP(
            from_file=self.filepath,
            from_clauses=self.clauses
        )


__all__ = [
    'CNFSCIP',
    'CNFSCIPData',
    'Clause',
    'Clauses'
]
