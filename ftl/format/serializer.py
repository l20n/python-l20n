from . import ast

class Serializer():
    def serialize(self, ast):
        string = ''
        for entry in ast.body:
            string += self.dumpEntry(entry) + '\n'
        return string

    def dumpEntry(self, entry):
        if entry.type == 'Entity':
            return self.dumpEntity(entry)
        elif entry.type == 'Comment':
            return self.dumpComment(entry) + '\n'
        elif entry.type == 'Section':
            return self.dumpSection(entry)

    def dumpEntity(self, entity):
        str = ''

        if entity.comment:
            str += self.dumpComment(entity.comment) + '\n'

        id = self.dumpIdentifier(entity.id)
        value = self.dumpPattern(entity.value)

        if len(entity.traits):
            traits = self.dumpTraits(entity.traits, 2)
            str += '{} = {}\n{}'.format(id, value, traits)
        else:
            str += '{} = {}'.format(id, value)
        return str

    def dumpComment(self, comment):
        return '#{}'.format(comment.content.replace('\n', '\n# '))

    def dumpSection(self, section):
        comment = '{}\n'.format(
            self.dumpComment(section.comment)) if section.comment else ''
        sec = self.dumpIdentifier(section.name)
        return '{}[[ {} ]]'.format(comment, sec)

    def dumpIdentifier(self, id):
        if id.namespace:
            return '{}/{}'.format(id.namespace, id.name)
        return id.name

    def dumpPattern(self, pattern):
        if pattern is None:
            return ''
        if pattern._quoteDelim:
            return '"{}"'.format(pattern.source)
        str = ''

        for elem in pattern.elements:
            if elem.type == 'TextElement':
                if '\n' in elem.value:
                    str += '\n | {}'.format(elem.value.replace('\n', '\n | '))
                else:
                    str += elem.value
            elif elem.type == 'Placeable':
                str += self.dumpPlaceable(elem)
        return str

    def dumpPlaceable(self, placeable):
        source = ', '.join(map(self.dumpExpression, placeable.expressions))

        if source.endswith('\n'):
            return '{{ {}}}'.format(source)
        return '{{ {} }}'.format(source)

    def dumpExpression(self, exp):
        if exp.type == 'ExternalArgument':
            return '${}'.format(exp.name)
        elif exp.type == 'BuiltinReference':
            return exp.name
        elif exp.type == 'EntityReference':
            return self.dumpIdentifier(exp)
        elif exp.type == 'SelectExpression':
            sel = self.dumpExpression(exp.expression)
            traits = self.dumpTraits(exp.variants, 2)
            return '{} ->\n{}\n'.format(sel, traits)
        elif exp.type == 'CallExpression':
            id = self.dumpExpression(exp.callee)
            args = self.dumpCallArgs(exp.args)
            return '{}({})'.format(id, args)
        elif exp.type == 'Pattern':
            return self.dumpPattern(exp)
        elif exp.type == 'Number':
            return exp.value
        elif exp.type == 'MemberExpression':
            obj = self.dumpExpression(exp.object)
            key = self.dumpExpression(exp.keyword)
            return '{}[{}]'.format(obj, key)
        elif exp.type == 'Identifier':
            return self.dumpIdentifier(exp)

    def dumpCallArgs(self, args):
        return ', '.join(map(
            lambda arg: '{}:{}'.format(arg.name, self.dumpExpression(arg.value))
                if arg.type == 'KeyValueArg' else self.dumpExpression(arg),
            args))

    def dumpTraits(self, traits, indent):
        px = ' ' * indent
        return '\n'.join(map(lambda trait: '{}{}[{}] {}'.format(
            px, 
            '*' if trait.default else '',
            self.dumpIdentifier(trait.key),
            self.dumpPattern(trait.value)
        ), traits))
