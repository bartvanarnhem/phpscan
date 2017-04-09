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
    def process_op(self, compare_op, value_op, sign=-1):
        id = compare_op.id
        data_type = value_op.data_type
        value = value_op.value

        self.establish_var_value(id, data_type, value)


class IsSmallerHandler(OpcodeHandler):
    def process_op(self, compare_op, value_op, sign=1):
        id = compare_op.id
        data_type = value_op.data_type
        value = value_op.value - 1 * sign

        self.establish_var_value(id, data_type, value)



satisfier_handlers = [
    ('ZEND_IS_EQUAL', IsEqualHandler),
    ('ZEND_IS_IDENTICAL', IsEqualHandler),

    ('ZEND_ISSET_ISEMPTY_DIM_OBJ', UninitializedPropertyAccessHandler),
    ('ZEND_FETCH_DIM_R', UninitializedPropertyAccessHandler),

    ('ZEND_IS_SMALLER', IsSmallerHandler),
    ('ZEND_IS_SMALLER_OR_EQUAL', IsSmallerHandler)
]
