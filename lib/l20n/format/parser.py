import re


class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

MAX_PLACEABLES = 100


class Parser():
    _patterns = {
        'complexId': re.compile(r'[A-Za-z_][\w\.]*'),
        'identifier': re.compile(r'[A-Za-z_]\w*'),
    }

    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        return self.getL20n()

    def parseString(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        ast, overlay = self.getString(string[0], 1)

        if overlay:
            return {
              'v': ast,
              't': 'overlay'
            }
        else:
            return ast

    def getL20n(self):
        ast = []

        self.getWS()

        while self._index < self._length:
            ast.append(self.getEntry())
            if self._index < self._length:
                self.getWS()
        return ast

    def getEntry(self):
        # 66 === '<'
        if ord(self._source[self._index]) == 60:
            self._index += 1
            id = self.getIdentifier()
            if self._index < self._length:
                cc = ord(self._source[self._index])
            else:
                cc = None
            # 91 === '['
            if cc == 91:
                self._index += 1
                return self.getEntity(id,
                                      self.getItemList(self.getExpression,
                                                       ']'))
            return self.getEntity(id, None)
        raise self.error('Invalid entry')

    def getEntity(self, id, index):
        entity = {'$i': id}

        if index:
            entity['$x'] = index

        if not self.getRequiredWS():
            raise self.error('Expected white space')

        if self._length > self._index:
            ch = self._source[self._index]
        else:
            ch = None
        value = self.getValue(index is None, ch)
        attrs = None

        if value is None:
            if ch == '>':
                raise self.error('Expected ">"')
            attrs = self.getAttributes()
        else:
            entity['$v'] = value
            ws1 = self.getRequiredWS()
            if not self._source[self._index] == '>':
                if not ws1:
                    raise self.error('Expected ">"')
                attrs = self.getAttributes()

        self._index += 1
        if attrs:
            for key in attrs:
                entity[key] = attrs[key]

        return entity

    def getValue(self, optional=False, ch=None, index=None):
        overlay = False

        if ch is None:
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                ch = None
        if ch == "'" or ch == '"':
            val = self.getString(ch, 1)
            overlay = val[1]
            val = val[0]
        elif ch == '{':
            val = self.getHash()
        else:
            if not optional:
                raise self.error('Unknown value type')
            return None

        if index or overlay:
            value = {}
            value['v'] = val

            if index:
                value['x'] = index
            if overlay:
                value['t'] = 'overlay'
            return value
        return val

    def getWS(self):
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])

    def getRequiredWS(self):
        pos = self._index
        if self._length > self._index:
            cc = ord(self._source[self._index])
        else:
            return False

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])
        return pos != self._index

    def getIdentifier(self):
        reId = self._patterns['identifier']

        match = reId.match(self._source[self._index:])

        if not match:
            raise self.error('Identifier has to start with [a-zA-Z_]')

        self._index += match.end()
        return match.group(0)

    def getComplexId(self):
        reId = self._patterns['complexId']

        match = reId.match(self._source[self._index:])

        if not match:
            raise self.error('Identifier has to start with [a-zA-Z_]')

        self._index += match.end()
        return match.group(0)

    def getString(self, opchar, opcharLen):
        opcharPos = self._source.find(opchar, self._index + opcharLen)

        if opcharPos == -1:
            raise self.error('Unclosed literal string')
        buf = self._source[self._index + opcharLen: opcharPos]

        testPos = buf.find('{{')
        if testPos != -1:
            return self.getComplexString(opchar, opcharLen)

        testPos = buf.find('\\')
        if testPos != -1:
            return self.getComplexString(opchar, opcharLen)

        self._index = opcharPos + opcharLen
        return [buf, self.isOverlay(buf)]

    def getAttributes(self):
        attrs = {}

        while True:
            attr = self.getKVPWithIndex()
            attrs[attr[0]] = attr[1]
            ws1 = self.getRequiredWS()
            ch = self._source[self._index]
            if ch == '>':
                break
            elif not ws1:
                raise self.error('Expected ">"')
        return attrs

    def getKVP(self):
        key = self.getIdentifier()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return [key, self.getValue()]

    def getKVPWithIndex(self, type=None):
        key = self.getIdentifier()
        index = []

        if self._source[self._index] == '[':
            self._index += 1
            self.getWS()
            index = self.getItemList(self.getExpression, ']')
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return [key, self.getValue(False, None, index)]

    def getHash(self):
        self._index += 1
        self.getWS()
        defItem = None
        hi = None
        comma = None
        hash = {}

        while True:
            isDefItem = False
            if self._source[self._index] == '*':
                self._index += 1
                if defItem is not None:
                    raise self.error('Default item redefinition forbidden')
                isDefItem = True
            hi = self.getKVP()
            hash[hi[0]] = hi[1]
            if isDefItem:
                defItem = hi[0]
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

        if defItem is not None:
            hash['__default'] = defItem
        return hash

    def unescapeString(self):
        self._index += 1
        ch = self._source[self._index]
        if ch == 'u':
            ucode = ''
            for i in range(0, 4):
                self._index += 1
                ch = self._source[self._index]
                cc = ord(ch[0])
                if (cc > 96 and cc < 103) or \
                   (cc > 64 and cc < 71) or \
                   (cc > 47 and cc < 58):
                    ucode += ch
                else:
                    raise self.error('Illegal unicode escape sequence')
            return unichr(int(ucode, 16))
        return ch

    def isOverlay(self, string):
        overlay = False

        testPos = string.find('<')

        if testPos != -1 and string[testPos + 1] != ' ':
            overlay = True
        else:
            testPos = string.find('&')
            if testPos != -1 and string[testPos + 1] != ' ':
                overlay = True

        return overlay

    def getComplexString(self, opchar, opcharLen):
        body = None
        buf = ''
        placeables = 0
        overlay = False

        self._index += opcharLen - 1

        walkChars = True
        while walkChars:
            self._index += 1
            ch = self._source[self._index]
            if ch == '\\':
                buf += self.unescapeString()
            elif ch == '{' and self._source[self._index + 1] == '{':
                    if body is None:
                        body = []
                    if placeables > MAX_PLACEABLES - 1:
                        raise self.error(
                            'Too many placeables, maximum allowed is ' +
                            MAX_PLACEABLES)
                    if buf:
                        if self.isOverlay(buf):
                            overlay = True
                        body.append(buf)
                    self._index += 2
                    self.getWS()
                    body.append(self.getExpression())
                    self.getWS()
                    if self._source[self._index] != '}' or \
                       self._source[self._index + 1] != '}':
                        raise self.error('Expected "}}"')
                    self._index += 1
                    placeables += 1

                    buf = ''
            else:
                if ch == opchar:
                    self._index += 1
                    walkChars = False
                else:
                    buf += ch
                    if self._index + 1 >= self._length:
                        raise self.error('Unclosed string literal')

        if body is None:
            return [buf, self.isOverlay(buf)]
        if len(buf):
            if self.isOverlay(buf):
                overlay = True
            body.append(buf)
        return [body, overlay]

    def getExpression(self):
        exp = self.getPrimaryExpression()

        self.getWS()

        if self._source[self._index] == '(':
            self._index += 1
            return self.getCallExpression(exp)
        return exp

    def getCallExpression(self, callee):
        self.getWS()
        exp = {}

        exp['t'] = 'call'
        exp['v'] = callee
        exp['a'] = self.getItemList(self.getExpression, ')')

        return exp

    def getPrimaryExpression(self):
        cc = ord(self._source[self._index])

        prim = {}

        # variable: $
        if cc == 36:
            self._index += 1
            prim['t'] = 'var'
            prim['v'] = self.getComplexId()
        # global: @
        elif cc == 64:
            self._index += 1
            prim['t'] = 'glob'
            prim['v'] = self.getComplexId()
        else:
            prim['t'] = 'id'
            prim['v'] = self.getIdentifier()

        return prim

    def getItemList(self, callback, closeChar):
        self.getWS()
        if self._source[self._index] == closeChar:
            self._index += 1
            return []

        items = []

        while True:
            items.append(callback())
            self.getWS()

            ch = self._source[self._index]
            if ch == ',':
                self._index += 1
                self.getWS()
            elif ch == closeChar:
                self._index += 1
                break
            else:
                raise self.error('Expected "," or "' + closeChar + '"')

        return items

    def error(self, message, pos=None):
        if pos is None:
            pos = self._index
        start = self._source.rfind('<', pos - 1)
        lastClose = self._source.rfind('>', pos - 1)
        start = lastClose + 1 if lastClose > start else start
        context = self._source[start:pos + 10]

        msg = '%s at pos %s: "%s"' % (message, pos, context)
        return ParserError(msg, pos, context)
