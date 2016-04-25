from . import ast

class SerializerError(Exception):
    def __init__(self, message, pos = 0, context = None):
        self.name = 'SerializerError'
        self.message = message
        self.pos = pos
        self.context = context

class Serializer():
    def serialize(self, resource):
        string = ''
        for entry in resource.body:
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
        if isinstance(entry, ast.Entity):
            return self.dumpEntity(entry)
        if isinstance(entry, ast.Comment):
            return self.dumpComment(entry)

    def dumpEntity(self, entity):
        ident = self.dumpIdentifier(entity.id)
        index = self.dumpIndex(entity.index) if entity.index else ''
        val = self.dumpValue(entity.value, 0)

        if len(entity.attrs) == 0:
            return '<' + ident + index + ' ' + val + '>'
        else:
            return '<' + ident + index + ' ' + val + \
                    '\n' + self.dumpAttributes(entity.attrs) + '>'

    def dumpIdentifier(self, ident):
        return ident.name

    def dumpValue(self, value, depth):
        if value is None:
            return ''

        if isinstance(value, ast.String):
            return self.dumpString(value)

        if isinstance(value, ast.Hash):
            return self.dumpHash(value, depth)

    def dumpString(self, string):
        ret = '"'

        for chunk in string.content:
            if type(chunk) is str or type(chunk) is unicode:
                ret += chunk.replace('"', '\\"')
            else:
                ret += '{{ ' + self.dumpExpression(chunk) + ' }}'
        return ret + '"'

    def dumpAttributes(self, attrs):
        string = ''

        for attr in attrs:
            if attr.index:
                string += '  ' + self.dumpIdentifier(attr.id) + \
                    self.dumpIndex(attr.index) + ': ' + \
                    self.dumpValue(attr.value, 1) + '\n'
            else:
                string += '  ' + self.dumpIdentifier(attr.id) + ': ' + \
                    self.dumpValue(attr.value, 1) + '\n'
        return string

    def dumpExpression(self, exp):
        if isinstance(exp, ast.CallExpression):
            return self.dumpCallExpression(exp)
        elif isinstance(exp, ast.PropertyExpression):
            return self.dumpPropertyExpression(exp)

        return self.dumpPrimaryExpression(exp)

    def dumpPropertyExpression(self, exp):
        idref = self.dumpExpression(exp.idref)

        if exp.computed:
            prop = self.dumpExpression(exp.exp)
            return '%s[%s]' % (idref, prop)
        
        prop = self.dumpIdentifier(exp.exp)
        return '%s.%s' % (idref, prop)

    def dumpCallExpression(self, exp):
        pexp = self.dumpExpression(exp.callee)

        attrs = self.dumpItemList(exp.args, self.dumpExpression)

        pexp += '(' + attrs + ')'
        return pexp

    def dumpPrimaryExpression(self, exp):
        ret = ''

        if type(exp) is str:
            return exp

        if isinstance(exp, ast.Global):
            ret += '@'
            ret += self.dumpIdentifier(exp.name)
        elif isinstance(exp, ast.Variable):
            ret += '$'
            ret += self.dumpIdentifier(exp.name)
        elif isinstance(exp, ast.Identifier):
            ret += self.dumpIdentifier(exp)
        else:
            raise SerializerError('Unknown primary expression')

        return ret

    def dumpHash(self, hashValue, depth):
        items = []
        string = ''

        for item in hashValue.items:
            indent = ' *' if item.default else '  '

            string = indent + self.dumpIdentifier(item.id) + ': ' + self.dumpValue(item.value, depth + 1)
            items.append(string)

        indent = '  ' * depth
        return '{\n' + indent + (',\n' + indent).join(items) + '\n' + indent + '}'

    def dumpItemList(self, itemList, cb):
        return ', '.join(map(cb, itemList))

    def dumpIndex(self, index):
        return '[' + self.dumpItemList(index, self.dumpExpression) + ']'

    def dumpComment(self, comment):
        return '/*%s*/' % comment.body

