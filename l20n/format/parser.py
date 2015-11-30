
from . import ast

class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

MAX_PLACEABLES = 100

class L20nParser():
    def parse(self, string):
        self.setContent(string)
        return self.getResource()

    def setContent(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)
        self._curEntryStart = 0

    def _getch(self):
        if self._index >= self._length:
            return ''
        return self._source[self._index]

    def _getnextch(self):
        self._index += 1
        if self._index >= self._length:
            return ''
        return self._source[self._index]

    def _getcc(self):
        if self._index >= self._length:
            return -1
        return ord(self._source[self._index])

    def _getnextcc(self):
        self._index += 1
        if self._index >= self._length:
            return -1
        return ord(self._source[self._index])

    def getResource(self):
        resource = ast.Resource()
        resource.setPosition(0, self._length)
        resource._errors = []
        junk = None

        self.getWS()
        while self._index < self._length:
            try:
                entry = self.getEntry()
                if junk:
                    resource._errors.append(self.parseError(junk))
                    resource.body.append(junk)
                    junk = None
                resource.body.append(entry)
            except ParserError:
                newjunk = self.getJunkEntry()
                if junk:
                    junk.content += newjunk.content
                    junk._pos['end'] = newjunk._pos['end']
                else:
                    junk = newjunk
            
            if self._index < self._length:
                self.getWS()

        if junk:
            resource._errors.append(self.parseError(junk))
            resource.body.append(junk)

        return resource

    def parseError(self, junk):
        parser = L20nParser()
        parser.setContent(junk.content)
        try:
            parser.getEntry()
        except ParserError as e:
            e.pos += junk._pos['start']
            return e

    def getEntry(self):
        self._curEntryStart = self._index

        if self._getch() == '<':
            self._index += 1
            id = self.getIdentifier()
            if self._getch() == '[':
                self._index += 1
                return self.getEntity(id,
                                      self.getItemList(self.getExpression,
                                                       ']'))
            return self.getEntity(id)

        if self._source.startswith('/*', self._index):
            return self.getComment()

        raise self.error('Invalid entry')

    def getEntity(self, id, index = None):
        if not self.getRequiredWS():
            raise self.error('Expected white space')

        ch = self._getch()
        hasIndex = index is not None
        value = self.getValue(ch, hasIndex, hasIndex)
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

    def getValue(self, ch = None, index = False, required = True):
        if ch is None:
            ch = self._source[self._index]

        if ch == "'" or ch == '"':
            return self.getString(ch, 1)
        elif ch == '{':
            return self.getHash(index)

        if required:
            raise self.error('Unknown value type')
        return None

    def getWS(self):
        cc = self._getcc()

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            cc = self._getnextcc()

    def getRequiredWS(self):
        pos = self._index
        cc = self._getcc()

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            cc = self._getnextcc()
        return pos != self._index

    def getIdentifier(self):
        start = self._index
        cc = self._getcc()

        # a-z | A-Z | _
        if (cc >= 97 and cc <= 122) or \
           (cc >= 65 and cc <= 90) or \
           cc == 95:
            cc = self._getnextcc()
        else:
            raise self.error('Identifier has to start with [a-zA-Z_]')

        # a-z | A-Z | 0-9 | _
        while (cc >= 97 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
              cc == 95:
            cc = self._getnextcc()

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
                if not self._source.startswith('}}', self._index):
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
        string._opchar = opchar

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
        index = None

        if self._source[self._index] == '[':
            self._index += 1
            self.getWS()
            index = self.getItemList(self.getExpression, ']')
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()

        hasIndex = index is not None
        attr = ast.Attribute(key, self.getValue(None, hasIndex), index)
        attr.setPosition(start, self._index)
        return attr

    def getHash(self, index):
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

        if not index:
            if not any(item.default for item in items):
                raise self.error('Unresolvable Hash Value')

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

        propExpr = ast.PropertyExpression(idref, exp, computed)
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
            variable = ast.Variable(self.getIdentifier())
            variable.setPosition(start, self._index)
            return variable
        elif ch == '@':
            self._index += 1
            glob = ast.Global(self.getIdentifier())
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

        start = self._source.rfind('<', 0, pos - 1)
        lastClose = self._source.rfind('>', 0, pos - 1)
        start = lastClose + 1 if lastClose > start else start
        context = self._source[start : pos + 10]

        msg = '%s at pos %s: "%s"' % (message, pos, context)
        return ParserError(msg, pos, context)

    def getJunkEntry(self):
        pos = self._curEntryStart + 1
        nextEntity = self._source.find('<', pos)
        if nextEntity < 0:
            nextEntity = self._length
        nextComment = self._source.find('/*', pos)
        if nextComment < 0:
            nextComment = self._length

        nextEntry = min(nextEntity, nextComment)

        self._index = nextEntry

        junk = ast.JunkEntry(self._source[self._curEntryStart : nextEntry])
        junk.setPosition(self._curEntryStart, nextEntry)
        return junk
