import argparse
from phpscan.core import Scan, logger, verify_dependencies
from phpscan.satisfier.greedy import GreedySatisfier

INITIAL_STATE = {
    '_POST': {
        'type': 'array'
    },
    '_REQUEST': {
        'type': 'array'
    },
    '_GET': {
        'type': 'array'
    },
    '_COOKIE': {
        'type': 'array'
    }
}

PHP_LOADER = 'php_loader/phpscan.php'


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

        scan.initial_state = INITIAL_STATE
        scan.php_loader_location = PHP_LOADER
        scan.satisfier = GreedySatisfier()

        scan.start()

        scan.print_results()
