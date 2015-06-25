
import ast

class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

MAX_PLACEABLES = 100


class L20nParser():
    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)
        self._curEntryStart = 0;

        return self.getResource()

    def getResource(self):
        resource = ast.Resource()
        resource.setPosition(0, self._length)

        self.getWS()
        while self._index < self._length:
            try:
                resource.body.append(self.getEntry())
            except ParserError as e:
                print(e)
                resource.body.append(self.getJunkEntry())
            
            if self._index < self._length:
                self.getWS()

        return resource

    def getEntry(self):
        self._curEntryStart = self._index

        if self._source[self._index] == '<':
            self._index += 1
            id = self.getIdentifier()
            if self._source[self._index] == '[':
                self._index += 1
                return self.getEntity(id,
                                      self.getItemList(self.getExpression,
                                                       ']'))
            return self.getEntity(id)

        if self._source[self._index: self._index + 1] == '/*':
            return self.getComment()

        raise self.error('Invalid entry')

    def getEntity(self, id, index = None):
        if not self.getRequiredWS():
            raise self.error('Expected white space')

        ch = self._source[self._index]
        value = self.getValue(ch)
        attrs = None
        
        if value == None:
            if ch == '>':
                raise self.error('Expected ">"')
            attrs = self.getAttributes()
        else:
            ws1 = self.getRequiredWS()
            if not self._source[self._index] == '>':
                if not ws1:
                    raise self.error('Expected ">"')
                attrs = self.getAttributes()

        self._index += 1

        entity = ast.Entity(id, value, index, attrs)
        entity.setPosition(self._curEntryStart, self._index)
        return entity

    def getValue(self, ch):
        if ch is None:
            ch = self._source[self._index]

        if ch == "'" or ch == '"':
            val = self.getString(ch, 1)
        elif ch == '{':
            val = self.getHash()

        return val

    def getWS(self):
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            cc = ord(self._source[self._index])

    def getRequiredWS(self):
        pos = self._index
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            cc = ord(self._source[self._index])
        return pos != self._index

    def getIdentifier(self):
        start = self._index
        cc = ord(self._source[self._index])

        # a-z | A-Z | _
        if (cc >= 97 and cc <= 122) or \
           (cc >= 65 and cc <= 90) or \
           cc == 95:
            self._index += 1
            cc = ord(self._source[self._index])
        else:
            raise self.error('Identifier has to start with [a-zA-Z_]')

        # a-z | A-Z | 0-9 | _
        while (cc >= 97 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
              cc == 95:
            self._index += 1
            cc = ord(self._source[self._index])

        id = ast.Identifier(self._source[start : self._index])
        id.setPosition(start, self._index)
        return id

    def getUnicodeChar(self):
        for i in range(0, 4):
            self._index += 1
            cc = ord(self._source[self._index])
            if (cc > 96 and cc < 103) or \
               (cc > 64 and cc < 71) or \
               (cc > 47 and cc < 58):
                continue
            raise self.error('Illegal unicode escape sequence')
        return '\\u' + self._source[self._index - 3 : self._index + 1]

    def getString(self, opchar, opcharLen):
        body = []
        buf = ''
        placeables = 0

        self._index += opcharLen - 1

        start = self._index + 1

        closed = False

        while not closed:
            self._index += 1
            ch = self._source[self._index]
            if ch == '\\':
                self._index += 1
                ch2 = self._source[self._index]
                if ch2 == 'u':
                    buf += self.getUnicodeChar()
                elif ch2 == opchar or ch2 == '\\':
                    buf += ch2
                elif (ch2 == '{' and self._source[self._index + 1] == '{'):
                    buf += '{'
                else:
                    raise self.error('Illegal unicode escape sequence')
            elif ch == '{' and self._source[self._index + 1] == '{':
                if placeables > MAX_PLACEABLES - 1:
                    raise self.error(
                        'Too many placeables, maximum allowed is ' +
                        MAX_PLACEABLES)
                if len(buf):
                    body.append(buf)
                    buf = ''
                self._index += 2
                self.getWS()
                body.append(self.getExpression())
                self.getWS()
                if self._source[self._index : self._index + 1] != '}}':
                    raise self.error('Expected "}}"')
                self._index += 1
                placeables += 1
            else:
                if ch == opchar:
                    self._index += 1
                    closed = True
                else:
                    buf += ch
                    if self._index + 1 >= self._length:
                        raise self.error('Unclosed string literal')

        if len(buf):
            body.append(buf)

        string = ast.String(self._source[start : self._index - 1], body)
        string.setPosition(start, self._index)

        return string

    def getAttributes(self):
        attrs = []

        while True:
            attr = self.getAttribute()
            attrs.append(attr)
            ws1 = self.getRequiredWS()
            ch = self._source[self._index]
            if ch == '>':
                break
            elif not ws1:
                raise self.error('Expected ">"')
        return attrs

    def getAttribute(self):
        start = self._index
        key = self.getIdentifier()

        if self._source[self._index] == '[':
            self._index += 1
            self.getWS()
            index = self.getItemList(self.getExpression, ']')
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()

        attr = ast.Attribute(key, self.getValue(), index)
        attr.setPosition(start, self._index)
        return attr

    def getHash(self):
        start = self._index
        items = []

        self._index += 1
        self.getWS()

        while True:
            items.append(self.getHashItem())
            self.getWS()

            comma = self._source[self._index] == ','
            if comma:
                self._index += 1
                self.getWS()

            if self._source[self._index] == '}':
                self._index += 1
                break
            if not comma:
                raise self.error('Expected "}"')

        hash = ast.Hash(items)
        hash.setPosition(start, self._index)
        return hash

    def getHashItem(self):
        start = self._index

        defItem = False
        if self._source[self._index] == '*':
            self._index += 1
            defItem = True

        key = self.getIdentifier()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()

        hashItem = ast.HashItem(key, self.getValue(), defItem)
        hashItem.setPosition(start, self._index)
        return hashItem

    def getComment(self):
        self._index += 2
        start = self._index
        end = self._source.find('*/', start)

        if end == -1:
            raise self.error('Comment without closing tag')

        self._index = end + 2
        comment = ast.Comment(self._source[start : end])
        comment.setPosition(start - 2, self._index)
        return comment

    def getExpression(self):
        start = self._index
        exp = self.getPrimaryExpression()

        while True:
            ch = self._source[self._index]
            if ch == '.' or ch == '[':
                self._index += 1
                exp = self.getPropertyExpression(exp, ch == '[', start)
            elif ch == '(':
                self._index += 1
                exp = self.getCallExpression(exp, start)
            else:
                break

        return exp

    def getPropertyExpression(self, idref, computed, start):
        if computed:
            self.getWS()
            exp = self.getExpression()
            self.getWS()
            if self._source[self._index] != ']':
                raise self.error('Expected "]"')
            self._index += 1
        else:
            exp = self.getIdentifier()

        propExpr = ast.PropertyExpresion(idref, exp, computed)
        propExpr.setPosition(start, self._index)
        return propExpr

    def getCallExpression(self, callee, start):
        self.getWS()

        callExpr = ast.CallExpression(callee,
            self.getItemList(self.getExpression, ')'))
        callExpr.setPosition(start, self._index)
        return callExpr

    def getPrimaryExpression(self):
        start = self._index
        ch = self._source[self._index]

        if ch == '$':
            self._index += 1
            variable = ast.Variable(self.getIdentifier)
            variable.setPosition(start, self._index)
            return variable
        elif ch == '@':
            self._index += 1
            glob = ast.Global(self.getIdentifier)
            glob.setPosition(start, self._index)
            return glob
        else:
            return self.getIdentifier()

    def getItemList(self, callback, closeChar):
        items = []
        closed = False

        self.getWS()

        if self._source[self._index] == closeChar:
            self._index += 1
            closed = True

        while not closed:
            items.append(callback())
            self.getWS()
            ch = self._source[self._index]
            if ch == ',':
                self._index += 1
                self.getWS()
            elif ch == closeChar:
                self._index += 1
                closed = True
            else:
                raise self.error('Expected "," or "' + closeChar + '"')

        return items

    def error(self, message):
        pos = self._index

        start = self._source.rfind('<', pos - 1)
        lastClose = self._source.rfind('>', pos - 1)
        start = lastClose + 1 if lastClose > start else start
        context = self._source[start : pos + 10]

        msg = '%s at pos %s: "%s"' % (message, pos, context)
        return ParserError(msg, pos, context)

    def getJunkEntry(self):
        pos = self._index
        nextEntity = self._source.find('<', pos)
        nextComment = self._source.find('/*', pos)

        nextEntry = min(nextEntity, nextComment)

        if nextEntry == -1:
            nextEntry = self._length

        self._index = nextEntry

        return ast.JunkEntry(self._source[self._curEntryStart : nextEntry])

l20nCode = '<id "value">'

l20nParser = L20nParser()
ast = l20nParser.parse(l20nCode)

import json
print(json.dumps(ast.toJSON(), indent=2))
