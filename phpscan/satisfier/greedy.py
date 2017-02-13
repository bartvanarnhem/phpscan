from ..opcode import zend_opcode_list, zend_opcode_lookup
from ..core import Logger, logger
from satisfier import Satisfier, OpcodeHandler
import json


class GreedySatisfier(Satisfier):

    def __init__(self):
        global satisfier_handlers
        Satisfier.__init__(self, satisfier_handlers)

        self.register_handlers(satisfier_handlers)

    def register_handlers(self, handlers):
        for handler in handlers:
            self.register_handler(handler[1](handler[0], self))


class UninitializedPropertyAccessHandler(OpcodeHandler):

    def __init__(self, opcode_name, satisfier):
        OpcodeHandler.__init__(self, opcode_name, satisfier)

    def process_op(self, compare_op, value_op, sign=-1):
        state_var = self.satisfier.start_state.get_var_ref(compare_op.id)
        property_name = value_op.value

        if not 'properties' in state_var:
            state_var['properties'] = {}

        if not property_name in state_var['properties']:
            state_var['properties'][property_name] = {
                'type': 'string',
                'value': ''
            }


class IsEqualHandler(OpcodeHandler):

    def __init__(self, operand_name, satisfier):
        OpcodeHandler.__init__(self, operand_name, satisfier)

    def process_op(self, compare_op, value_op, sign=-1):
        var = self.satisfier.start_state.get_var_ref(compare_op.id)

        var['type'] = value_op.data_type
        var['value'] = value_op.value


class IsSmallerHandler(OpcodeHandler):

    def __init__(self, opcode_name, satisfier):
        OpcodeHandler.__init__(self, opcode_name, satisfier)

    def process_op(self, compare_op, value_op, sign=1):
        var = self.satisfier.start_state.get_var_ref(compare_op.id)
        value = value_op.value

        var['type'] = value_op.data_type
        var['value'] = value - 1 * sign


satisfier_handlers = [
    ('ZEND_IS_EQUAL', IsEqualHandler),
    ('ZEND_IS_IDENTICAL', IsEqualHandler),

    ('ZEND_ISSET_ISEMPTY_DIM_OBJ', UninitializedPropertyAccessHandler),
    ('ZEND_FETCH_DIM_R', UninitializedPropertyAccessHandler),

    ('ZEND_IS_SMALLER', IsSmallerHandler),
    ('ZEND_IS_SMALLER_OR_EQUAL', IsSmallerHandler)
]
