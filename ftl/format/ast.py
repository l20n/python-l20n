import json

def attr2json(attr):
    if isinstance(attr, Node):
        return attr.toJSON()
    elif isinstance(attr, list):
        return [attr2json(i) for i in attr]
    else:
        return attr

class Node(object):
    def __init__(self):
        self.type = self.__class__.__name__

    def toJSON(self):
        fields = {}
        for key in vars(self):
            if key[0] == '_':
                continue
            attr = getattr(self, key)
            fields[key] = attr2json(attr)
        return fields

    def __str__(self):
        return json.dumps(self.toJSON())

    def setPosition(self, start, end):
        self._pos = {
            "start": start,
            "end": end
        }

class Resource(Node):
    def __init__(self):
        super(Resource, self).__init__()
        self.body = []

class Entry(Node):
    def __init__(self):
        super(Entry, self).__init__()

class Identifier(Node):
    def __init__(self, name, namespace):
        super(Identifier, self).__init__()
        self.name = name
        self.namespace = namespace

class Section(Node):
    def __init__(self, name, comment = None):
        super(Section, self).__init__()
        self.name = name
        self.comment = comment

class Pattern(Node):
    def __init__(self, source, elements):
        super(Pattern, self).__init__()
        self.source = source
        self.elements = elements

class Member(Node):
    def __init__(self, key, value, default = False):
        super(Member, self).__init__()
        self.key = key
        self.value = value
        self.default = default

class Entity(Entry):
    def __init__(self, id, value = None, traits = None, comment = None):
        super(Entity, self).__init__()
        self.id = id
        self.value = value
        self.traits = traits or []
        self.comment = comment 


class Placeable(Node):
    def __init__(self, expression):
        super(Placeable, self).__init__()
        self.expression = expression

class SelectExpression(Node):
    def __init__(self, expression, variants = None):
        super(SelectExpression, self).__init__()
        self.expression = expression
        self.variants = variants

class MemberExpression(Node):
    def __init__(self, obj, keyword):
        super(MemberExpression, self).__init__()
        self.obj = obj
        self.keyword = keyword

class CallExpression(Node):
    def __init__(self, callee, args):
        super(CallExpression, self).__init__()
        self.callee = callee
        self.args = args

class ExternalArgument(Node):
    def __init__(self, name):
        super(ExternalArgument, self).__init__()
        self.name = name

class KeyValueArg(Node):
    def __init__(self, name, value):
        super(KeyValueArg, self).__init__()
        self.name = name
        self.value = value

class EntityReference(Identifier):
    def __init__(self, name, namespace):
        super(EntityReference, self).__init__(name, namespace)

class BuiltinReference(Identifier):
    def __init__(self, name, namespace):
        super(BuiltinReference, self).__init__(name, namespace)

class Keyword(Identifier):
    def __init__(self, name, namespace = None):
        super(Keyword, self).__init__(name, namespace)

class Number(Node):
    def __init__(self, value):
        super(Number, self).__init__()
        self.value = value

class TextElement(Node):
    def __init__(self, value):
        super(TextElement, self).__init__()
        self.value = value

class Comment(Node):
    def __init__(self, content):
        super(Comment, self).__init__()
        self.content = content

class JunkEntry(Node):
    def __init__(self, content):
        super(JunkEntry, self).__init__()
        self.content = content
