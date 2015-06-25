import json

def attr2json(attr):
    if isinstance(attr, Node):
        return attr.toJSON()
    elif isinstance(attr, list):
        return [attr2json(i) for i in attr]
    else:
        return attr

class Node:
    def __init__(self):
        self.type = self.__class__.__name__

    def toJSON(self):
        fields = {}
        for key in vars(self):
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
        super().__init__()

class Identifier(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class Variable(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class Global(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

class Value(Node):
    def __init__(self):
        super().__init__()

class String(Value):
    def __init__(self, source, content):
        super().__init__()
        self.source = source
        self.content = content

class Hash(Value):
    def __init__(self, items):
        super().__init__()
        self.items = items

class Entity(Entry):
    def __init__(self, id, value = None, index = None, attrs = None):
        super().__init__()
        self.id = id
        self.value = value
        self.index = index
        self.attrs = attrs or []

class Resource(Node):
    def __init__(self, body = None):
        super().__init__()
        self.body = body or []

class Attribute(Node):
    def __init__(self, id, value, index = None):
        super().__init__()
        self.id = id
        self.value = value
        self.index = index

class HashItem(Node):
    def __init__(self, id, value, defItem):
        super().__init__()
        self.id = id
        self.value = value
        self.default = defItem

class Comment(Node):
    def __init__(self, body):
        super().__init__()
        self.body = body

class Expression(Node):
    def __init__(self):
        super().__init__()

class PropertyExpression(Expression):
    def __init__(self, idref, exp, computed = False):
        super().__init__()
        self.idref = idref
        self.exp = exp
        self.computed = computed

class CallExpression(Expression):
    def __init__(self, callee, args):
        super().__init__()
        self.callee = callee
        self.args = args

class JunkEntry(Node):
    def __init__(self, content):
        super().__init__()
        self.content = content
