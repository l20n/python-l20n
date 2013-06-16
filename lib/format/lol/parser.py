import string

class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

class Parser():


    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        return self.getLOL()

    def getAttributes(self):
        attrs = []
        while True:
            attr = self.getKVPWithIndex('Attribute')
            attr['local'] = attr['key']['name'][0] == '_'
            attrs.append(attr)
            ws1 = self.getRequiredWS()
            ch = self._source[self._index]
            if ch == '>':
                break
            elif not ws1:
                raise self.error('Expected ">"')
        return attrs

    def getKVP(self, type):
        key = self.getIdentifier()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return {
            'type': type,
            'key': key,
            'value': self.getValue()
        }

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
        return {
            'type': type,
            'key': key,
            'value': self.getValue(),
            'index': index
        }

    def getHash(self):
        self._index += 1
        self.getWS()
        if self._source[self._index] == '}':
            self._index += 1
            return {
                'type': 'Hash',
                'content': []
            }

        hasDefItem = False
        hash = []
        while True:
            defItem = False
            if self._source[self._index] == '*':
                self._index += 1
                if hasDefItem:
                    raise error('Default item redefinition forbidden')
                defItem = True
                hasDefItem = True
            hi = self.getKVP('HashItem')
            hi['default'] = defItem
            hash.append(hi)
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
        return {
            'type': 'Hash',
            'content': hash
        }

    def getString(self, opchar):
        l = len(opchar)
        self._index += l
        start = self._index
        
        close = self._source.find(opchar, start)
        while close != -1 and \
              ord(self._source[close - 1]) == 92 and \
              ord(self._source[close - 2]) != 92:
            close = self._source.find(opchar, close + 1)
        if close == -1:
            raise self.error('Unclosed string literal')
        s = self._source[start:close]
        self._index = close + l

        # \\ | \' | \" | \{{
        s = s.replace('\\\\', '\\');
        s = s.replace('\\\'', '\'');
        s = s.replace('\\"', '"');
        s = s.replace('\{{', '{{');

        return {
            'type': 'String',
            'content': s,
            'isNotComplex': s.find('{{') == -1  # why || undefined in js?
        }

    def getValue(self, optional=False, ch=None):
        if ch is None:
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                ch = None
        if ch == "'" or ch == '"':
            if ch == self._source[self._index + 1] and \
               ch == self._source[self._index + 2]:
                return self.getString(ch*3)
            return self.getString(ch)
        if ch == '{':
            return self.getHash()
        if not optional:
            raise self.error('Unknown value type')
        return None

    def getWS(self, wschars=string.whitespace):
        if self._length > self._index:
            ch = self._source[self._index]
        else:
            return False

        while ch in wschars:
            self._index += 1
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                break

    def getRequiredWS(self, wschars=string.whitespace):
        if self._length > self._index:
            ch = self._source[self._index]
        else:
            return False

        ws = False
        while ch in wschars:
            ws = True
            self._index += 1
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                break

        return ws

    def getVariable(self):
        self._index += 1
        return {
            'type': 'VariableExpression',
            'id': self.getIdentifier()
        }

    def getIdentifier(self):
        index = self._index
        start = index
        source = self._source
        l = len(source)
        if index < l:
            cc = ord(source[start])
        else:
            cc = -1

        if (cc < 97 or cc > 122) and \
           (cc < 65 or cc > 90) and \
           cc != 95:
            raise self.error('Identifier has to start with [a-zA-Z_]')

        while (cc >= 95 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
              cc == 95:
            index += 1
            if l <= index:
                break
            cc = ord(source[index])

        self._index = index

        return {
            'type': 'Identifier',
            'name': source[start:index]
        }

    def getMacro(self, id):
        if id['name'][0] == '_':
            raise error('Macro ID cannot start with "_"')
        self._index += 1
        idlist = self.getItemList(self.getVariable, ')')
        self.getRequiredWS()

        if self._source[self._index] != '{':
            raise self.error('Expected "{"')
        self._index += 1
        self.getWS()
        exp = self.getExpression()
        self.getWS()
        if self._source[self._index] != '}':
            raise self.error('Expected "}"')
        self._index += 1
        self.getWS()
        if ord(self._source[self._index]) != 62:
            raise self.error('Expected ">"')
        self._index += 1
        return {
            'type': 'Macro',
            'id': id,
            'args': idlist,
            'expression': exp
        }

    def getEntity(self, id, index):
        if not self.getRequiredWS():
            raise self.error('Expected white space')

        if self._length > self._index:
            ch = self._source[self._index]
        else:
            ch = None
        value = self.getValue(True, ch)
        attrs = []
        if value is None:
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
        return {
            'type': 'Entity',
            'id': id,
            'value': value,
            'index': index,
            'attrs': attrs,
            'local': (ord(id['name'][0]) == 95)
        }

    def getEntry(self):
        cc = ord(self._source[self._index])

        if cc == 60:
            self._index += 1
            id = self.getIdentifier()
            if self._index < self._length:
                cc = ord(self._source[self._index])
            else:
                cc = None

            if cc == 40:
                return self.getMacro(id)
            if cc == 91:
                self._index += 1
                return self.getEntity(id,
                                      self.getItemList(self.getExpression, ']'))
            return self.getEntity(id, [])
        raise self.error('Invalid entry')

    def getLOLPlain(self):
        entries = []

        self.getWS()

        while self._index < self._length:
            entries.append(self.getEntry())
            if self._index < self._length:
                self.getWS()
        return {
          'type': 'LOL',
          'body': entries
        }

    getLOL = getLOLPlain

    def getExpression(self):
        return self.getConditionalExpression()

    def getPrefixExpression(self, token, cl, op, nxt):
        exp = nxt()

        while True:
            t = ''
            self.getWS()
            ch = self._source[self._index]
            if ch not in token[0]:
                break
            t += ch
            self._index += 1
            if len(token) > 1:
                pass
            self.getWS()
            exp = {
                'type': cl,
                'operator': {
                    'type': op,
                    'token': t
                },
                'left': exp,
                'right': nxt()
            }
        return exp

    def getConditionalExpression(self):
        exp = self.getAdditiveExpression()
        self.getWS()
        if ord(self._source[self._index]) != 63:
            return exp
        self._index += 1
        self.getWS()
        consequent = self.getExpression()
        self.getWS()
        if ord(self._source[self._index]) != 58:
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return {
            'type': 'ConditionalExpression',
            'test': exp,
            'consequent': consequent,
            'alternate': self.getExpression()
        }

    def getAdditiveExpression(self):
        return self.getPrefixExpression([['+', '-']],
                                        'BinaryExpression',
                                        'BinaryOperator',
                                        self.getPrimaryExpression)

    def getPrimaryExpression(self):
        pos = self._index
        cc = ord(self._source[pos])

        while cc > 47 and cc < 58:
            pos += 1
            cc = ord(self._source[pos])
        if pos > self._index:
            start = self._index
            self._index = pos
            return {
                'type': 'Number',
                'value': int(self._source[start: pos])
            }

        if cc in [39, 34, 123, 91]:
            return self.getValue()

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
                raise self.error('Expected "," or "%s"' % closeChar)
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
