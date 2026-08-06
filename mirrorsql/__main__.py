"""python -m mirrorsql <root> -- print the MIRROR-SQL corpus summary as JSON."""
import argparse
import json
import sys

from .corpus import Corpus


def main() -> int:
    ap = argparse.ArgumentParser(prog="mirrorsql")
    ap.add_argument("root")
    args = ap.parse_args()
    print(json.dumps(Corpus(args.root).summary(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
