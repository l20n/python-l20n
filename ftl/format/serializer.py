from . import ast

class FTLSerializer():
    def serialize(self, ast):
        body = ast['body']
        comment = ast['comment']

        string = ''
        if comment is not None:
            string += self.dumpComment(comment) + '\n\n'
        for entry in body:
            string += self.dumpEntry(entry)
        return string

    def dumpEntry(self, entry):
        if entry['type'] == 'Entity':
            return self.dumpEntity(entry) + '\n'
        elif entry['type'] == 'Comment':
            return self.dumpComment(entry) + '\n\n'
        elif entry['type'] == 'Section':
            return self.dumpSection(entry) + '\n'
        elif entry['type'] == 'JunkEntry':
            return ''
        else:
            print(entry)
            raise Exception('Unknown entry type.')
        return ''

    def dumpEntity(self, entity):
        str = ''

        if entity['comment']:
            str += self.dumpComment(entity['comment']) + '\n'

        id = self.dumpIdentifier(entity['id'])
        value = self.dumpPattern(entity['value'])

        if len(entity['traits']):
            traits = self.dumpMembers(entity['traits'], 2)
            str += '{} = {}\n{}'.format(id, value, traits)
        else:
            str += '{} = {}'.format(id, value)
        return str

    def dumpComment(self, comment):
        return '# {}'.format(comment['content'].replace('\n', '\n# '))

    def dumpSection(self, section):
        comment = '{}\n'.format(
            self.dumpComment(section['comment'])) if section['comment'] else ''
        sec = self.dumpKeyword(section['key'])
        str = '{}[[ {} ]]\n\n'.format(comment, sec)

        for entry in section['body']:
            str += self.dumpEntry(entry)
        return str


    def dumpIdentifier(self, id):
        return id['name']

    def dumpKeyword(self, kw):
        if kw['namespace']:
            return '{}/{}'.format(kw['namespace'], kw['name'])
        return kw['name']

    def dumpPattern(self, pattern):
        if pattern is None:
            return ''
        if pattern['_quoteDelim']:
            return '"{}"'.format(pattern['source'])
        str = ''

        for elem in pattern['elements']:
            if elem['type'] == 'TextElement':
                if '\n' in elem['value']:
                    str += '\n | {}'.format(elem['value'].replace('\n', '\n | '))
                else:
                    str += elem['value']
            elif elem['type'] == 'Placeable':
                str += self.dumpPlaceable(elem)
        return str

    def dumpPlaceable(self, placeable):
        source = ', '.join(map(self.dumpExpression, placeable['expressions']))

        if source.endswith('\n'):
            return '{{ {}}}'.format(source)
        return '{{ {} }}'.format(source)

    def dumpExpression(self, exp):
        if exp['type'] == 'Identifier' or \
           exp['type'] == 'BuiltinReference' or \
           exp['type'] == 'EntityReference':
            return self.dumpIdentifier(exp)
        if exp['type'] == 'ExternalArgument':
            return '${}'.format(self.dumpIdentifier(exp))
        elif exp['type'] == 'SelectExpression':
            sel = self.dumpExpression(exp['expression'])
            variants = self.dumpMembers(exp['variants'], 2)
            return '{} ->\n{}\n'.format(sel, variants)
        elif exp['type'] == 'CallExpression':
            id = self.dumpExpression(exp['callee'])
            args = self.dumpCallArgs(exp['args'])
            return '{}({})'.format(id, args)
        elif exp['type'] == 'Pattern':
            return self.dumpPattern(exp)
        elif exp['type'] == 'Number':
            return exp['value']
        elif exp['type'] == 'Keyword':
            return self.dumpKeyword(exp)
        elif exp['type'] == 'MemberExpression':
            obj = self.dumpExpression(exp['object'])
            key = self.dumpExpression(exp['keyword'])
            return '{}[{}]'.format(obj, key)

    def dumpCallArgs(self, args):
        return ', '.join(map(
            lambda arg: '{}: {}'.format(arg['name'],
                                       self.dumpExpression(arg['value']))
                if arg['type'] == 'KeyValueArg' else self.dumpExpression(arg),
            args))

    def dumpMembers(self, members, indent):
        return '\n'.join(map(lambda member: '{}[{}] {}'.format(
            ' ' * (indent - 1) + '*' if member['default'] else ' ' * indent,
            self.dumpExpression(member['key']),
            self.dumpPattern(member['value'])
        ), members))
