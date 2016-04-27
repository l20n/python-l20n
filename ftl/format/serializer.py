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
        else:
            str += '{} = {}'.format(id, value)
        return str

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
        return str()
