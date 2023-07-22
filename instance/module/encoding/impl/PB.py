from threading import Lock
from typing import List, Tuple, Dict, Any

from instance.module.variables.vars import Supplements
from ..encoding import Encoding, EncodingData

Coef = int
Lit = int
Term = Tuple[Coef, Lit]
PBConstraint = Tuple[List[Term], int]
PBConstraints = List[PBConstraint]

pb_data = {}
parse_lock = Lock()


class PBData(EncodingData):
    def __init__(self, pb_constraints: PBConstraints, lines: str = None, max_lit: int = None):
        self._lines = lines
        self._pb_constraints = pb_constraints
        self._max_lit = max_lit

    def pb_constraints(self) -> PBConstraints:
        return self._pb_constraints

    def _get_lines_and_max_lit(self) -> Tuple[str, int]:
        if not self._lines or not self._max_lit:
            lines, max_lit = [], 0
            for pb_constraint in self._pb_constraints:
                max_lit = PB.get_max_lit(pb_constraint)
                lines.append(PB.to_string(pb_constraint) + '\n')
            self._lines, self._max_lit = ''.join(lines), max_lit
        return self._lines, self._max_lit

    def _get_source_header(self, payload_len: int) -> str:
        lines, max_lit = self._get_lines_and_max_lit()
        return f'* #variable={max_lit} #constraint={len(self._pb_constraints) + payload_len}\n'

    def source(self, supplements: Supplements = ((), ())) -> str:
        assumptions, constraints = supplements
        assert constraints == [], "constraints should be empty"
        lines, max_lit = self._get_lines_and_max_lit()
        payload_len = len(constraints) + len(assumptions)
        return ''.join([
            self._get_source_header(payload_len),
            lines, *(f'1 x{x} >= 1;\n' if x > 0 else f'-1 x{abs(x)} >= 0;\n' for x in assumptions)
        ])

    @property
    def max_literal(self) -> int:
        return self._get_lines_and_max_lit()[1]


class PB(Encoding):
    slug = 'encoding:pb'
    comment_lead = ['p', 'c', '*']

    def __init__(self, from_pb_constraints: PBConstraints = None, from_file: str = None):
        super().__init__(from_file)
        self.pb_constraints = from_pb_constraints

    @staticmethod
    def to_string(pb_constraint: PBConstraint):
        terms, b = pb_constraint
        line = ""
        de = 0
        for coef, lit in terms:
            assert lit != 0
            if lit < 0:
                line += str(-1 * coef) + " " + "x" + str(abs(lit)) + " "
                de -= coef
            else:
                line += str(coef) + " " + "x" + str(abs(lit)) + " "
        line += ">= " + str(b + de)
        return line

    @staticmethod
    def get_max_lit(pb_constraint: PBConstraint) -> int:
        terms, b = pb_constraint
        max_lit = 0
        for _, lit in terms:
            max_lit = max(max_lit, abs(lit))
        return max_lit

    @staticmethod
    def parse_line_opb(words) -> PBConstraint:
        i = 0
        terms: List[Term] = []
        while words[i] != ">=" and i < len(words):
            assert words[i + 1].startswith('x')
            lit = int(words[i + 1][1:])
            assert lit > 0
            terms.append((int(words[i]), lit))
            i += 2
        assert words[i] == ">="
        i += 1
        b: int = int(words[i][:-1])
        return terms, b

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

            pb_data[self.filepath] = PBData(
                pb_constraints, ''.join(lines), max_lit
            )
        except Exception as exc:
            msg = f'Error while parsing encoding file in line {process_line}'
            raise ValueError(msg) from exc

    def _process_raw_data(self):
        with parse_lock:
            if self.filepath in pb_data:
                return

            data = self.get_raw_data()
            self._parse_raw_data(data)

    def get_data(self) -> PBData:
        if self.pb_constraints:
            return PBData(self.pb_constraints)
        elif self.filepath in pb_data:
            return pb_data[self.filepath]

        self._process_raw_data()
        return pb_data[self.filepath]

    def __copy__(self):
        return PB(
            from_file=self.filepath,
            from_pb_constraints=self.pb_constraints
        )

    def __config__(self) -> Dict[str, Any]:
        return {
            'slug': self.slug,
            'from_file': self.filepath,
            'from_pb_clauses': self.pb_constraints,
        }


__all__ = [
    'PB',
    'PBData',
    # types
    'PBConstraint',
    'PBConstraints'
]
