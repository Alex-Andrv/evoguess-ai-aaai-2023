from threading import Lock
from typing import List, Tuple

from pyscipopt.scip import Model, PY_SCIP_PARAMSETTING

from .PB import PB, PBData

Coef = int
Lit = int
Term = Tuple[Coef, Lit]
PBConstraint = Tuple[List[Term], int]
PBConstraints = List[PBConstraint]

pb_data = {}
parse_lock = Lock()


class PBSCIPData(PBData):
    def __init__(self, pb_constraints: PBConstraints, lines: str = None, max_lit: int = None):
        super().__init__(pb_constraints, lines, max_lit)

        model = Model()

        assert max_lit != None

        for lit in range(1, max_lit + 1):
            model.addVar(vtype='B', name=str(lit))

        model.hideOutput()
        model.setParam('display/verblevel', 0)

        for pb_constraint in self._pb_constraints:
            terms, b = pb_constraint
            line = -b
            for term in terms:
                var = model.getVars()[term[1] - 1]
                line += term[0] * var
            model.addCons(line >= 0)

        model.setPresolve(PY_SCIP_PARAMSETTING.AGGRESSIVE)
        model.presolve()
        model.setPresolve(PY_SCIP_PARAMSETTING.DEFAULT)
        assert len(model.getVars()) == max_lit, "presolver shrink vars"
        self.model = model

    def get_model(self):
        return self.model


class PBSCIP(PB):
    slug = 'encoding:pb:PBSCIP'

    def _parse_raw_data(self, raw_data: str):
        process_line = 1
        try:
            lines, pb_constraints, max_lit = [], [], 0
            for line in raw_data.splitlines(keepends=True):
                if line[0] not in self.comment_lead:
                    words = line.split()
                    pb_constraint = self.parse_line_opb(words)
                    max_lit = max(max_lit, self.get_max_lit(pb_constraint))
                    pb_constraints.append(pb_constraint)
                    lines.append(line)
                process_line += 1

            pb_data[self.filepath] = PBSCIPData(
                pb_constraints, ''.join(lines), max_lit
            )
        except Exception as exc:
            msg = f'Error while parsing encoding file in line {process_line}'
            raise ValueError(msg) from exc

    def get_data(self) -> PBSCIPData:
        if self.pb_constraints:
            return PBSCIPData(self.pb_constraints)
        elif self.filepath in pb_data:
            return pb_data[self.filepath]

        self._process_raw_data()
        return pb_data[self.filepath]

    def __copy__(self):
        return PBSCIP(
            from_file=self.filepath,
            from_pb_constraints=self.pb_constraints
        )


__all__ = [
    'PBSCIP',
    'PBSCIPData',
    # types
    'PBConstraint',
    'PBConstraints'
]
