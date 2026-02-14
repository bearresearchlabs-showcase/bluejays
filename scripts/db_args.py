"""Shared database argument parsing for scripts. Supports db-N, N, range, -a, --all."""

from typing import List


def parse_db_args(args: List[str]) -> List[int]:
    """Parse database arguments. Returns list of db numbers (1-16).
    Supports: db-1, db-5, 1, 5, db-1 db-5 (range), -a, --all.
    """
    db_nums: List[int] = []
    if not args:
        return []

    if "-a" in args or "--all" in args:
        return list(range(1, 17))

    if "--help" in args or "-h" in args:
        return []

    for arg in args:
        arg = str(arg).strip()
        if arg.startswith("db-"):
            try:
                db_nums.append(int(arg.split("db-")[1]))
            except (ValueError, IndexError):
                continue
        elif arg.isdigit():
            db_nums.append(int(arg))

    if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
        db_nums = list(range(db_nums[0], db_nums[1] + 1))

    return sorted(set(db_nums))
