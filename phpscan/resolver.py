from core import Logger, logger

class Resolver(object):
    def __init__(self, transforms, state):
        self._transforms = transforms
        self._state = state
        self.register_resolvers()

    def register_resolvers(self):
        self._resolver = dict()
        global RESOLVERS
        for resolver in RESOLVERS:
            self.register_resolver(resolver[0], resolver[1](resolver[0], self))

    def register_resolver(self, function_name, resolver):
        self._resolver[function_name] = resolver

    def is_tracking(self, var_id):
        return var_id in self._transforms

    def resolve(self, var_id, data_type):
        condition = {}

        if self._state.is_tracking(var_id):
            condition = {
                'type': 'base_var',
                'id': var_id
            }
        elif self.is_tracking(var_id):
            transform = self._transforms[var_id]
            function_name = transform['function']

            if function_name in self._resolver:
                condition = self._resolver[function_name].process(data_type, transform['args'])
                if 'args' in condition:
                    for i in range(len(condition['args'])):
                        if condition['args'][i]['type'] == 'symbolic':
                            condition['args'][i] = self.resolve(condition['args'][i]['id'],
                                                                data_type)

            else:
                msg = 'Not processing %s (no resolver)' % function_name
                logger.log(msg, '', Logger.DEBUG)
                raise Exception(msg)
        else:
            raise Exception('Cannot resolve value for untracked id \'%s\'.' % var_id)

        return condition

class TransformResolver(object):
    def __init__(self, function_name, resolver):
        self._name = function_name
        self._resolver = resolver

    def process(self, data_type, args):
        logger.log('Processing %s...' % self._name, '', Logger.DEBUG)
        return self.resolve(data_type, args)

    def resolve(self, data_type, args):
        raise Exception('resolve should be implemented in child class')


class SubstrResolver(TransformResolver):
    def resolve(self, data_type, args):
        return {
            'type': 'extract',
            'args': args
        }

class FetchDimResolver(TransformResolver):
    def resolve(self, data_type, args):
        (var_arg, idx_arg) = args

        if var_arg['type'] == 'symbolic':
            if self._resolver.is_tracking(var_arg['id']):
                transform = self._resolver._transforms[var_arg['id']]

                if transform['function'] == 'explode':
                    return {
                        'type': 'explode',
                        'args': transform['args'],
                        'index': idx_arg['value']
                    }


        return {
            'type': 'base_var',
            'id': args[0]
        }



RESOLVERS = [
    ('substr', SubstrResolver),
    ('fetch_dim_r', FetchDimResolver)
]
