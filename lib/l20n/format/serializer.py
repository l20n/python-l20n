
class SerializerError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'SerializerError'
        self.message = message
        self.pos = pos
        self.context = context

class Serializer():
    def serialize(self, ast):
        string = ''
        for entry in ast:
            string += self.dumpEntry(entry) + '\n'
        return string

    def serializeString(self, ast):
        string = ''

        if type(ast) is dict:
            string += self.dumpValue(ast, 0)
        else:
            string += self.dumpString(ast)

        return string

    def dumpEntry(self, entry):
        return self.dumpEntity(entry)

    def dumpEntity(self, entity):
        ident = ''
        index = ''
        val = ''
        attrs = {}

        for key in entity.keys():
            if key == '$v':
                val = entity['$v']
            elif key == '$x':
                index = self.dumpIndex(entity['$x'])
            elif key == '$i':
                ident = self.dumpIdentifier(entity['$i'])
            else:
                attrs[key] = entity[key]

        if len(attrs) == 0:
            return '<' + ident + index + ' ' + self.dumpValue(val, 0) + '>'
        else:
            return '<' + ident + index + ' ' + self.dumpValue(val, 0) + \
                    '\n' + self.dumpAttributes(attrs) + '>'

    def dumpIdentifier(self, ident):
        return ident

    def dumpValue(self, value, depth):
        if value is None:
            return ''

        if type(value) is str or type(value) is unicode:
            return self.dumpString(value)

        if type(value) is list:
            return self.dumpComplexString(value)

        if type(value) is dict:
            if 't' in value and value['t'] == 'overlay':
                return self.dumpValue(value['v'], depth)
            return self.dumpHash(value, depth)

    def dumpString(self, string):
        return '"' + string.replace('"', '\\"') + '"'

    def dumpComplexString(self, chunks):
        string = '"'

        for chunk in chunks:
            if type(chunk) is str or type(chunk) is unicode:
                string += chunk.replace('"', '\\"')
            else:
                string += '{{ ' + self.dumpExpression(chunk) + ' }}'
        return string + '"'

    def dumpAttributes(self, attrs):
        string = ''

        for key, attr in attrs.items():
            if 'x' in attr:
                string += '  ' + key + self.dumpIndex(attr['x']) + ': ' + \
                        self.dumpValue(attr['v'], 1) + '\n'
            else:
                string += '  ' + key + ': ' + self.dumpValue(attr, 1) + '\n'
        return string

    def dumpExpression(self, exp):
        if exp['t'] == 'call':
            return self.dumpCallExpression(exp)
        elif exp['t'] == 'prop':
            return self.dumpPropertyExpression(exp)

        return self.dumpPrimaryExpression(exp)

    def dumpPropertyExpression(self, exp):
        prop = self.dumpExpression(exp['p'])
        idref = self.dumpExpression(exp['e'])

        return '%s[%s]' % (idref, prop)

    def dumpCallExpression(self, exp):
        pexp = self.dumpPrimaryExpression(exp['v'])

        attrs = self.dumpItemList(exp['a'], self.dumpExpression)

        pexp += '(' + attrs + ')'
        return pexp

    def dumpPrimaryExpression(self, exp):
        ret = ''

        if exp['t'] == 'glob':
            ret += '@'
            ret += exp['v']
        elif exp['t'] == 'var':
            ret += '$'
            ret += exp['v']
        elif exp['t'] == 'id':
            ret += exp['v']
        else:
            raise SerializerError('Unknown primary expression')

        return ret

    def dumpHash(self, hashValue, depth):
        items = []
        string = ''

        defIndex = None

        if '__default' in hashValue:
            defIndex = hashValue['__default']

        for key in hashValue.keys():
            indent = '  '
            if key[0:2] == '__':
                continue

            if key == defIndex:
                indent = ' *'
            string = indent + key + ': ' + self.dumpValue(hashValue[key], depth + 1)
            items.append(string)

        indent = '  ' * depth
        return '{\n' + indent + (',\n' + indent).join(items) + '\n' + indent + '}'

    def dumpItemList(self, itemList, cb):
        return ', '.join(map(cb, itemList))

    def dumpIndex(self, index):
        return '[' + self.dumpItemList(index, self.dumpExpression) + ']'

