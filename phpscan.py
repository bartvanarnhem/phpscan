import argparse
from phpscan.core import Scan, logger, verify_dependencies
from phpscan.satisfier.greedy import GreedySatisfier

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', help='increase verbosity (0 = results only, 1 = show progress, 2 = debug', type=int, choices=[0, 1, 2], default=0)
    parser.add_argument(
        'entrypoint', help='the PHP application entrypoint', default='index.php')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()

    if verify_dependencies():
        logger.verbosity = args.verbose

        scan = Scan(args.entrypoint)

        scan.satisfier = GreedySatisfier()

        scan.start()

        scan.print_results()
