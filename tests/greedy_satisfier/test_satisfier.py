import pytest

import sys
sys.path.append('../..')

from phpscan.core import Scan, logger, verify_dependencies
from phpscan.satisfier.greedy import GreedySatisfier


def init_and_run_simple_scan(script):
    scan = Scan(script, Scan.INPUT_MODE_SCRIPT)

    scan.satisfier = GreedySatisfier()

    scan.start()

    return scan    


def test_string_comparison():
    scan = init_and_run_simple_scan("if ($_GET['var'] == 'value') phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_integer_comparison():
    scan = init_and_run_simple_scan("if ($_GET['var'] == 10) phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_greater_than():
    scan = init_and_run_simple_scan("if ($_GET['var'] > 10) phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_smaller_than():
    scan = init_and_run_simple_scan("if ($_GET['var'] < 10) phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_indirect_assign():
    scan = init_and_run_simple_scan("$a = $_GET['var']; if ($a == 'value') phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_substring():
    scan = init_and_run_simple_scan("$a = substr($_GET['var'], 2, 3); if ($a == 'lu') phpscan_flag('flag');")
    assert scan.has_reached_case('flag')


def test_negate():
    scan = init_and_run_simple_scan("if (!($a == 'value')) phpscan_flag('flag');")
    assert scan.has_reached_case('flag')

def test_explode():
    script = """
        $a = explode('.', $_GET['var']);
        $class = $a[0];
        $action = $a[1];

        if (($class == 'auth') && ($action == 'login')) {
            phpscan_flag('flag');
        }
        """
    scan = init_and_run_simple_scan(script)
    assert scan.has_reached_case('flag')

def test_concat():
    script = """
        $a = $_GET['var'];
        $b = $a . 'lue';

        if ($b === 'value') {
            phpscan_flag('flag');
        }
        """
    scan = init_and_run_simple_scan(script)
    assert scan.has_reached_case('flag')

def test_add():
    script = """
        $a = $_GET['var'];
        $b = $a + 7;

        if ($b === 10) {
            phpscan_flag('flag');
        }
        """
    scan = init_and_run_simple_scan(script)
    assert scan.has_reached_case('flag')
