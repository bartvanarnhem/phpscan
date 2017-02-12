import copy
import uuid
import collections
import subprocess
import json
import re
from opcode import Operand


def verify_dependencies():
    ok = True

    if not verify_zend_extension_enabled():
        print 'FATAL: PHPSCan Zend module is not properly installed'
        ok = False

    return ok

def verify_zend_extension_enabled():
    proc = subprocess.Popen(['php', '-r', 'print phpscan_enabled();'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output_stdout = proc.stdout.read()
    output_stderr = proc.stderr.read()

    return not 'Call to undefined function phpscan_enabled' in output_stdout + output_stderr

class Logger:
    STANDARD = 0
    PROGRESS = 1
    DEBUG = 2

    def __init__(self, verbosity=STANDARD):
        self.verbosity = verbosity

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def state(self, value):
        self._verbosity = value

    def log(self, section, content, min_level=0):
        if self.verbosity >= min_level:
            if section:
                print section
            if content:
                print content
            print ''

logger = Logger()


class State:

    def __init__(self, state):
        self.state = state
        self._state_annotated = None
        self._lookup_map = None

        self.annotate()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def state_annotated(self):
        return self._state_annotated

    @property
    def hash(self):
        return make_hash(self.state)

    def fork(self):
        state_copy = copy.deepcopy(self.state)
        return State(state_copy)

    def is_tracking(self, op):
        return op.id in self._lookup_map

    def get_var_ref(self, id):
        return self._lookup_map[id]

    def annotate(self):
        self._lookup_map = dict()
        self._state_annotated = copy.deepcopy(self.state)

        self.annotate_recurse(self._state_annotated, self.state)

    def annotate_recurse(self, state_item_copy, state_item):
        for key in state_item_copy.keys():
            unique_id = str(uuid.uuid4())
            state_item_copy[key]['id'] = unique_id
            self._lookup_map[unique_id] = state_item[key]

            if 'properties' in state_item_copy[key]:
                self.annotate_recurse(
                    state_item_copy[key]['properties'], state_item[key]['properties'])

    def pretty_print(self):
        return self.pretty_print_recurse(self.state)

    def pretty_print_recurse(self, state_item, level=0):
        output = ''

        for var_name, var_info in state_item.iteritems():
            output += (' ' * 2 * level) + var_name + '\n'
            if 'properties' in var_info:
                output += self.pretty_print_recurse(
                    var_info['properties'], level + 1)
            if 'value' in var_info:
                indent = ' ' * 2 * (level + 1)
                output += '%svalue: %s (%s)\n' % (indent,
                                                  var_info['value'], var_info['type'])

        return output


class Scan:

    def __init__(self, php_file):
        self._php_file = php_file
        self._seen = set()
        self._queue = collections.deque()
        self._reached_cases = []

    @property
    def php_file(self):
        return self._php_file

    @property
    def initial_state(self):
        return self._initial_state

    @initial_state.setter
    def initial_state(self, value):
        self._initial_state = value

    @property
    def satisfier(self):
        return self._satisfier

    @satisfier.setter
    def satisfier(self, value):
        self._satisfier = value

    @property
    def php_loader_location(self):
        return self._php_loader_location

    @php_loader_location.setter
    def php_loader_location(self, value):
        self._php_loader_location = value

    def start(self):
        self._queue.append(State(self.initial_state))

        while len(self._queue) > 0:
            state = self._queue.popleft()

            if not self.is_state_seen(state):
                self.mark_state_seen(state)

                self.satisfier.start_state = state.fork()

                php_recorded_ops = self.process_state(
                    self.satisfier.start_state)
                sanitized_ops = self.sanitize_ops(php_recorded_ops)

                for new_state in self.satisfier.process(sanitized_ops):
                    self._queue.append(new_state)

        self.done()

    def done(self):
        pass

    def is_state_seen(self, state):
        return state.hash in self._seen

    def mark_state_seen(self, state):
        self._seen.add(state.hash)

    def process_state(self, state):
        logger.log(
            'Running with new input', state.pretty_print(), Logger.PROGRESS)

        ops = self.invoke_php(state, self._php_file)

        logger.log('PHP OPs', json.dumps(ops, indent=4), Logger.PROGRESS)

        return ops

    def sanitize_ops(self, ops):
        sanitized_ops = []

        for op in ops:
            op1 = Operand(
                op['op1_id'], op['op1_type'], op['op1_data_type'], op['op1_value'])
            op2 = Operand(
                op['op2_id'], op['op2_type'], op['op2_data_type'], op['op2_value'])

            sanitized_ops.append({
                'opcode': int(op['opcode']),
                'op1': op1,
                'op2': op2
            })

        return sanitized_ops

    def generate_php_initializer_code(self, state_json, php_file):

        state_json = state_json.replace('"', '\\"')

        code = '"include \\"%s\\"; phpscan_initialize(\'%s\'); include \\"%s\\";"' % (
            self.php_loader_location, state_json, php_file)

        return code

    def filter_php_response(self, category, output):
        result = None
        matches = re.search(
            r'__PHPSCAN_%s__(.*)__/PHPSCAN_%s__' % (category, category), output)

        if matches:
            result = matches.groups()[0]

        return result

    def invoke_php(self, state, php_file):
        state_json = json.dumps(state.state_annotated)

        code = self.generate_php_initializer_code(state_json, php_file)

        logger.log('Invoking PHP with', code, Logger.DEBUG)

        proc = subprocess.Popen(' '.join(
            ['php', '-r', code]), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        output_stdout = proc.stdout.read()
        output_stderr = proc.stderr.read()

        logger.log('PHP stdout', output_stdout, Logger.DEBUG)
        logger.log('PHP stderr', output_stderr, Logger.DEBUG)

        self.check_reached_cases(output_stdout, state)

        opcodes = self.filter_hit_ops(output_stdout)
        return opcodes

    def check_reached_cases(self, output, state):
        reached_cases = self.filter_php_response('FLAG', output)

        if reached_cases:
            self._reached_cases.append({
                'case': reached_cases,
                'state': state
            })

    def filter_hit_ops(self, output):
        opcodes = []
        opcode_json = self.filter_php_response('OPS', output)
        if opcode_json:
            opcodes = json.loads(opcode_json)

        return opcodes

    def print_results(self):
        for reached_case in self._reached_cases:
            print 'Successfully reached "%s" using input:' % reached_case['case']
            print reached_case['state'].pretty_print()


# http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """

    if isinstance(o, (set, tuple, list)):

        return tuple([make_hash(e) for e in o])

    elif not isinstance(o, dict):

        return hash(o)

    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(new_o.items()))))
