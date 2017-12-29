from ..opcode import ZEND_OPCODE_LIST, ZEND_OPCODE_LOOKUP
from ..core import Logger, logger
from satisfier import Satisfier, OpcodeHandler
import json


class GreedySatisfier(Satisfier):

    def __init__(self):
        global SATISFIER_HANDLERS
        Satisfier.__init__(self, SATISFIER_HANDLERS)

        self.register_handlers(SATISFIER_HANDLERS)

    def register_handlers(self, handlers):
        for handler in handlers:
            self.register_handler(handler[1](handler[0], self))


class UninitializedPropertyAccessHandler(OpcodeHandler):
    def process_op(self, compare_op, value_op, sign=-1):
        if self.satisfier.start_state.is_tracking(compare_op.id):
            state_var = self.satisfier.start_state.get_var_ref(compare_op.id)
            property_name = value_op.value

            state_var['type'] = 'array' # force this to be an array

            if not 'properties' in state_var:
                state_var['properties'] = {}

            if not property_name in state_var['properties']:
                # TODO should we name this differently?
                prop_id = 'fetch_dim_r(%s:%s)' % (compare_op.id, property_name)

                state_var['properties'][property_name] = {
                    'type': 'unknown',
                    'value': ''
                }

                self.satisfier.start_state._lookup_map[prop_id] = state_var['properties'][property_name]


            # TODO clean this up
            state_var = self.satisfier.start_state.get_annotated_var_ref(compare_op.id)
            property_name = value_op.value

            if not 'properties' in state_var:
                state_var['properties'] = {}

            if not property_name in state_var['properties']:
                prop_id = 'fetch_dim_r(%s:%s)' % (compare_op.id, property_name)

                state_var['properties'][property_name] = {
                    'type': 'unknown',
                    'value': '',
                    'id': prop_id,
                    'persistent_id': state_var['persistent_id'] + ':' + property_name
                }

                self.satisfier.start_state._annotated_lookup_map[prop_id] = state_var['properties'][property_name]



class IsEqualHandler(OpcodeHandler):
    def process_op(self, compare_op, value_op, sign=-1):
        var_id = compare_op.id
        data_type = value_op.data_type
        value = value_op.value

        # TODO: maybe remove
        # self.update_guessed_type_from_value(var_id, value)

        self.establish_var_value(var_id, data_type, value, 'equals')

class IsNotEqualHandler(OpcodeHandler):
    def process_op(self, compare_op, value_op, sign=-1):
        var_id = compare_op.id
        data_type = value_op.data_type
        value = value_op.value

        # TODO: maybe remove
        # self.update_guessed_type_from_value(var_id, value)

        self.establish_var_value(var_id, data_type, value, 'not_equals')

class IsSmallerHandler(OpcodeHandler):
    def process_op(self, compare_op, value_op, sign=1):
        var_id = compare_op.id
        data_type = value_op.data_type
        value = value_op.value

        # TODO: maybe remove
        # self.update_guessed_type_from_value(var_id, value)

        self.establish_var_value(var_id, data_type, value, 'smaller' if sign == 1 else 'greater')



SATISFIER_HANDLERS = [
    ('ZEND_IS_EQUAL', IsEqualHandler),
    ('ZEND_IS_IDENTICAL', IsEqualHandler),
    ('ZEND_IS_NOT_EQUAL', IsNotEqualHandler),
    ('ZEND_CASE', IsEqualHandler),

    ('ZEND_ISSET_ISEMPTY_DIM_OBJ', UninitializedPropertyAccessHandler),
    ('ZEND_FETCH_DIM_R', UninitializedPropertyAccessHandler),
    ('ZEND_FETCH_DIM_FUNC_ARG', UninitializedPropertyAccessHandler),


    ('ZEND_IS_SMALLER', IsSmallerHandler),
    ('ZEND_IS_SMALLER_OR_EQUAL', IsSmallerHandler)
]
