from enum import Enum
from typing import Tuple


class LogState(Enum):
    UP_TO_DATE = "up-to-date",
    SYNCHRONIZED = "synchronized",
    OUT_OF_DATE = "out-of-date"


def is_up_to_date(to_compare: Tuple[int, int], reference: Tuple[int, int]) -> LogState:
    cmp_term, cmp_log = to_compare
    ref_term, ref_log = reference
    if cmp_term > ref_term:
        return LogState.UP_TO_DATE
    elif cmp_term == ref_term and cmp_log > ref_log:
        return LogState.UP_TO_DATE
    elif cmp_term == ref_term and cmp_log == ref_log:
        return LogState.SYNCHRONIZED
    elif cmp_term == ref_term and cmp_log < ref_log:
        return LogState.OUT_OF_DATE
    elif cmp_term < ref_term:
        return LogState.OUT_OF_DATE
