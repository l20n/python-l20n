class FTLSerializer():
    def serialize(self, ast):
        body = ast['body']
        comment = ast['comment']

        string = u''
        if comment is not None:
            string += self.dumpComment(comment) + u'\n\n'
        for entry in body:
            string += self.dumpEntry(entry)
        return string

    def dumpEntry(self, entry):
        if entry['type'] == 'Entity':
            return self.dumpEntity(entry) + u'\n'
        elif entry['type'] == 'Comment':
            return self.dumpComment(entry) + u'\n\n'
        elif entry['type'] == 'Section':
            return self.dumpSection(entry) + u'\n'
        elif entry['type'] == 'JunkEntry':
            return u''
        else:
            print(entry)
            raise Exception('Unknown entry type.')
        return u''

    def dumpEntity(self, entity):
        str = u''

        if entity['comment']:
            str += u'\n' + self.dumpComment(entity['comment']) + u'\n'

        id = self.dumpIdentifier(entity['id'])
        str += u'{} ='.format(id)

        if (entity['value']):
            value = self.dumpPattern(entity['value'])
            str += u' {}'.format(value)

        if len(entity['traits']):
            traits = self.dumpMembers(entity['traits'], 2)
            str += u'\n{}'.format(traits)

        return str

    def dumpComment(self, comment):
        return u'# {}'.format(comment['content'].replace('\n', u'\n# '))

    def dumpSection(self, section):
        comment = u'{}\n'.format(self.dumpComment(
            section['comment'])) if section['comment'] else u''
        sec = self.dumpKeyword(section['key'])
        str = u'\n\n{}[[ {} ]]\n\n'.format(comment, sec)

        for entry in section['body']:
            str += self.dumpEntry(entry)
        return str

    def dumpIdentifier(self, id):
        return id['name']

    def dumpKeyword(self, kw):
        if kw['namespace']:
            return u'{}/{}'.format(kw['namespace'], kw['name'])
        return kw['name']

    def dumpPattern(self, pattern):
        if pattern is None:
            return u''
        str = u''

        for elem in pattern['elements']:
            if elem['type'] == 'TextElement':
                if '\n' in elem['value']:
                    str += u'\n  | {}'.format(
                        elem['value'].replace('\n', '\n  | '))
                else:
                    str += elem['value']
            elif elem['type'] == 'Placeable':
                str += self.dumpPlaceable(elem)

        if pattern['quoted']:
            return u'"{}"'.format(str)
        return str

    def dumpPlaceable(self, placeable):
        source = u', '.join(map(self.dumpExpression, placeable['expressions']))

        if source.endswith('\n'):
            return u'{{ {}}}'.format(source)
        return u'{{ {} }}'.format(source)

    def dumpExpression(self, exp):
        if exp['type'] == 'Identifier' or \
           exp['type'] == 'FunctionReference' or \
           exp['type'] == 'EntityReference':
            return self.dumpIdentifier(exp)
        if exp['type'] == 'ExternalArgument':
            return u'${}'.format(self.dumpIdentifier(exp))
        elif exp['type'] == 'SelectExpression':
            sel = self.dumpExpression(exp['expression'])
            variants = self.dumpMembers(exp['variants'], 2)
            return u'{} ->\n{}\n'.format(sel, variants)
        elif exp['type'] == 'CallExpression':
            id = self.dumpExpression(exp['callee'])
            args = self.dumpCallArgs(exp['args'])
            return u'{}({})'.format(id, args)
        elif exp['type'] == 'Pattern':
            return self.dumpPattern(exp)
        elif exp['type'] == 'Number':
            return exp['value']
        elif exp['type'] == 'Keyword':
            return self.dumpKeyword(exp)
        elif exp['type'] == 'MemberExpression':
            obj = self.dumpExpression(exp['object'])
            key = self.dumpExpression(exp['keyword'])
            return u'{}[{}]'.format(obj, key)

    def dumpCallArgs(self, args):
        return u', '.join(map(
            lambda arg:
                u'{}: {}'.format(arg['name'],
                                 self.dumpExpression(arg['value']))
                if arg['type'] == 'KeyValueArg' else self.dumpExpression(arg),
            args))

    def dumpMembers(self, members, indent):
        return u'\n'.join(map(lambda member: u'{}[{}] {}'.format(
            u' ' * (indent - 1) + u'*' if member['default'] else u' ' * indent,
            self.dumpExpression(member['key']),
            self.dumpPattern(member['value'])
        ), members))
