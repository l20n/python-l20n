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

class Entry(Node):
    def __init__(self):
        super(Entry, self).__init__()

class Identifier(Node):
    def __init__(self, name):
        super(Identifier, self).__init__()
        self.name = name

class Variable(Node):
    def __init__(self, name):
        super(Variable, self).__init__()
        self.name = name

class Global(Node):
    def __init__(self, name):
        super(Global, self).__init__()
        self.name = name

class Value(Node):
    def __init__(self):
        super(Value, self).__init__()

class String(Value):
    def __init__(self, source, content = None):
        super(String, self).__init__()
        self.source = source
        self.content = content or [source]

        self._opchar = '"'

class Hash(Value):
    def __init__(self, items = None):
        super(Hash, self).__init__()
        self.items = items or []

class Entity(Entry):
    def __init__(self, id, value = None, index = None, attrs = None):
        super(Entity, self).__init__()
        self.id = id
        self.value = value
        self.index = index
        self.attrs = attrs or []

class Resource(Node):
    def __init__(self, body = None):
        super(Resource, self).__init__()
        self.body = body or []

class Attribute(Node):
    def __init__(self, id, value, index = None):
        super(Attribute, self).__init__()
        self.id = id
        self.value = value
        self.index = index

class HashItem(Node):
    def __init__(self, id, value, defItem):
        super(HashItem, self).__init__()
        self.id = id
        self.value = value
        self.default = defItem

class Comment(Node):
    def __init__(self, body):
        super(Comment, self).__init__()
        self.body = body

class Expression(Node):
    def __init__(self):
        super(Expression, self).__init__()

class PropertyExpression(Expression):
    def __init__(self, idref, exp, computed = False):
        super(PropertyExpression, self).__init__()
        self.idref = idref
        self.exp = exp
        self.computed = computed

class CallExpression(Expression):
    def __init__(self, callee, args):
        super(CallExpression, self).__init__()
        self.callee = callee
        self.args = args

class JunkEntry(Node):
    def __init__(self, content):
        super(JunkEntry, self).__init__()
        self.content = content
