from core import Logger, logger

class Resolver:
    def __init__(self, transforms, state):
        self._transforms = transforms
        self._state = state
        self.register_resolvers()

    def register_resolvers(self):
        self._resolver = dict()
        global resolvers
        for resolver in resolvers:
            self.register_resolver(resolver[0], resolver[1](resolver[0])) 
    
    def register_resolver(self, function_name, resolver):
        self._resolver[function_name] = resolver

    def is_tracking(self, id):
        return id in self._transforms

    def resolve(self, id, data_type, value):
        if self._state.is_tracking(id):
            var = self._state.get_var_ref(id)

            var['type'] = data_type
            var['value'] = value
        elif self.is_tracking(id):
            transform = self._transforms[id]
            function_name = transform['function']

            if function_name in self._resolver:
                for parent_var in self._resolver[function_name].process(data_type, value, transform['args']):
                    (parent_id, parent_data_type, parent_value) = parent_var
                    self.resolve(parent_id, parent_data_type, parent_value)
            else:
                logger.log('Not processing %s (no resolver)' %
                        function_name, '', Logger.DEBUG)
        else:
            raise Exception('Cannot resolve value for untracked id \'%s\'.' % id)


class TransformResolver:
    def __init__(self, function_name):
        self._name = function_name
    
    def process(self, data_type, value, args):
        logger.log('Processing %s...' % self._name, '', Logger.DEBUG)
        return self.resolve(data_type, value, args)

    def resolve(self, data_type, value, args):
        raise Exception('resolve should be implemented in child class')


class SubstrTransformResolver(TransformResolver):
    def resolve(self, data_type, value, args):
        id = args[0]['id']
        value = '?' * args[1]['value'] + value
        yield (id, data_type, value)


resolvers = [
    ('substr', SubstrTransformResolver)
]
