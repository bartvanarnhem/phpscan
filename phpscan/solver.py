from core import Logger, logger
import z3
import json
import string
import uuid

class Solver(object):
    def __init__(self):
        self.register_adapters()
        self._base_var = {}

    def register_adapters(self):
        self._adapters = dict()
        global ADAPTERS
        for adapter in ADAPTERS:
            self.register_adapter(adapter[0], adapter[1](adapter[0], self))

    def register_adapter(self, op_name, adapter):
        self._adapters[op_name] = adapter


    def solve(self, state, conditions):
        self._state = state

        logger.log('CONDITIONS', json.dumps(conditions, indent=4), Logger.PROGRESS)

        solver = z3.Solver()
        self._solver = solver

        logger.log('BASE VARS', json.dumps(state._lookup_map, indent=4), Logger.PROGRESS)

        for var_id, var in state._lookup_map.iteritems():
            if var['type'] in ('string', 'unknown'):
                # Type could be unknown if newly discovered and we did not get a typehint yet
                self._base_var[var_id] = z3.String(var_id)
            elif var['type'] == 'integer':
                self._base_var[var_id] = z3.Int(var_id)
            else:
                logger.log('Ignoring unknown type %s while passing to Z3' %
                           var['type'], '', Logger.DEBUG)

        z3_solved = False

        try:
            for condition in conditions:
                solver.add(self.solve_rec(condition))

            solve_result = solver.check()
            logger.log('SOLVER RESULT', solve_result, Logger.PROGRESS)

            if solve_result == z3.sat:
                z3_solved = True
                model = solver.model()
                logger.log('SOLVER MODEL', model, Logger.PROGRESS)

                for var_id, var in self._base_var.iteritems():
                    var_ref = self._state.get_var_ref(var_id)
                    var_ref['value'] = self.get_z3_value(model[var])
        except z3.z3types.Z3Exception as e:
            print 'Got Z3Exception: %s' % str(e)

        # else:
        #     raise Exception('SOLVER COULD NOT SOLVE CONDITIONS')

    def get_z3_value(self, value):
        if z3.is_string(value):
            return value.as_string()[1:-1].replace('\\x00', '?')
        elif z3.is_int(value):
            return value.as_long()
        elif value is None:
            return '' # TODO adhere to type
        else:
            raise ValueError('Got unknown Z3 type')


    def solve_rec(self, condition):
        op_name = condition['type']
        if op_name in self._adapters:
            return self._adapters[op_name].process(condition)
        else:
            logger.log('Not processing %s (no adapter)' %
                       op_name, '', Logger.DEBUG)
            raise Exception('Not processing %s (no adapter)' % op_name)


class Z3Adapter(object):
    def __init__(self, op_name, solver):
        self._op_name = op_name
        self._solver = solver

    def process(self, args):
        logger.log('Processing %s...' % self._op_name, '', Logger.DEBUG)
        return self.adapt(args)

    def adapt(self, args):
        raise Exception('adapt should be implemented in child class')


class EqualsAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return self._solver.solve_rec(args[0]) == self._solver.solve_rec(args[1])

class NotEqualsAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return self._solver.solve_rec(args[0]) != self._solver.solve_rec(args[1])

class SmallerAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return self._solver.solve_rec(args[0]) < self._solver.solve_rec(args[1])

class GreaterAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return self._solver.solve_rec(args[0]) > self._solver.solve_rec(args[1])


class ExtractAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return z3.Extract(self._solver.solve_rec(args[0]), self._solver.solve_rec(args[1]),
                          self._solver.solve_rec(args[2]))


class ConcatAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']
        return z3.Concat(self._solver.solve_rec(args[0]), self._solver.solve_rec(args[1]))

class AddAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']

        return self._solver.solve_rec(args[0]) + self._solver.solve_rec(args[1])

class AssignAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']

        return self._solver.solve_rec(args[0])


class BaseVarAdapter(Z3Adapter):
    def adapt(self, condition):
        return self._solver._base_var[condition['id']]

class RawValueAdapter(Z3Adapter):
    def adapt(self, condition):
        value = condition['value']

        if isinstance(value, basestring):
            return z3.StringVal(value)
        elif isinstance(value, int):
            return value
        else:
            raise Exception('got unknown rawvalue')


def dimvar(var, idx):
    newvar = z3.String(str(uuid.uuid4()))
    # todo, split is now harcoded '.' -> this could also be a variable
    a = z3.parse_smt2_string('(assert (seq.in.re a (re.++ (re.loop (re.++ (re.* (re.union (re.range " " "-") (re.range "/" "~") ) ) (str.to.re ".")) %d 0 ) (str.to.re b) (re.* (re.++ (str.to.re ".") (re.* (re.range " " "~")) )) )))' % (idx), decls={'a': var, 'b': newvar})
    return (a, newvar)

class ExplodeAdapter(Z3Adapter):
    def adapt(self, condition):
        args = condition['args']

        (explode_constraint, var) = dimvar(self._solver.solve_rec(args[1]), condition['index'])
        self._solver._solver.add(explode_constraint)
        return var


ADAPTERS = [
    ('equals', EqualsAdapter),
    ('not_equals', NotEqualsAdapter),
    ('smaller', SmallerAdapter),
    ('greater', GreaterAdapter),
    ('extract', ExtractAdapter),
    ('concat', ConcatAdapter),
    ('add', AddAdapter),
    ('base_var', BaseVarAdapter),
    ('raw_value', RawValueAdapter),
    ('assign', AssignAdapter),
    ('explode', ExplodeAdapter)
]

