from ..opcode import ZEND_OPCODE_LIST, ZEND_OPCODE_LOOKUP
from ..core import Logger, logger
from ..resolver import Resolver
from ..solver import Solver

class Satisfier:

    def __init__(self, handlers):
        self._handlers = dict()
        self._start_state = None

    @property
    def start_state(self):
        return self._start_state

    @start_state.setter
    def start_state(self, value):
        self._start_state = value

    @property
    def resolver(self):
        return self._resolver

    @resolver.setter
    def resolver(self, value):
        self._resolver = value

    def is_tracking(self, operator):
        return self.start_state.is_tracking(operator.id) or self.resolver.is_tracking(operator.id)

    def process(self, ops, transforms):
        state = self.start_state
        state.conditions = []
        self.resolver = Resolver(transforms, self.start_state)

        for operator in ops:
            op1 = operator['op1']
            op2 = operator['op2']
            if self.is_tracking(op1) or self.is_tracking(op2):
                self.process_op(operator['opcode'], op1, op2)
            else:
                logger.log(
                    'Ignoring op on untracked operands', operator, Logger.DEBUG)

        solver = Solver()
        solver.solve(state, state.conditions)

        logger.log(
            'Resulted in new state', state.pretty_print(), Logger.PROGRESS)

        yield state

    def process_op(self, opcode, op1, op2):
        if opcode in self._handlers:
            self._handlers[opcode].process(op1, op2)
        else:
            logger.log('Not processing %s (no handler)' %
                       ZEND_OPCODE_LIST[opcode], '', Logger.DEBUG)

    def register_handler(self, handler):
        self._handlers[handler.opcode] = handler


class OpcodeHandler:

    def __init__(self, opcode_name, satisfier):
        self.opcode_name = opcode_name
        self.opcode = ZEND_OPCODE_LOOKUP[opcode_name]
        self.satisfier = satisfier

    def process(self, op1, op2):
        logger.log('Processing %s...' % self.opcode_name, '', Logger.DEBUG)

        if self.satisfier.is_tracking(op1):
            self.process_op(op1, op2)
        elif self.satisfier.is_tracking(op2):
            self.process_op(op2, op1, -1)
        else:
            raise Exception('Got to process for untracked operand')

    def process_op(self, compare_op, value_op, sign=-1):
        raise Exception('process_op should be implemented in child class')

    def establish_var_value(self, var_id, data_type, value, operator):
        r = {
            'type': operator,
            'args': [
                self.satisfier.resolver.resolve(var_id, data_type),
                {
                    'type': 'raw_value',
                    'value': value
                }
            ]
        }

        self.satisfier.start_state.conditions.append(r)

    def update_guessed_type_from_value(self, var_id, value):
        self.satisfier.start_state.update_guessed_type_from_value(var_id, value)

    @property
    def opcode(self):
        return self._opcode

    @opcode.setter
    def opcode(self, value):
        self._opcode = value

    @property
    def opcode_name(self):
        return self._opcode_name

    @opcode_name.setter
    def opcode_name(self, value):
        self._opcode_name = value

    @property
    def satisfier(self):
        return self._satisfier

    @satisfier.setter
    def satisfier(self, value):
        self._satisfier = value
