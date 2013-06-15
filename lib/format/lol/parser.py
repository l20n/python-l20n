
class Parser():


    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        return self.getLOL()

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
            raise Exception()
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

    def getValue(self, optional, ch=None):
        if ch is None:
            ch = self._source[self._index]
        if ch == "'" or ch == '"':
            if ch == self._source[self._index + 1] and \
               ch == self._source[self._index + 2]:
                return self.getString(ch*3)
            return self.getString(ch)

    def getRequiredWS(self):
        pos = self._index
        cc = ord(self._source[pos])
        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            cc = ord(self._source[self._index])
        return not self._index == pos

    def getWS(self):
        cc = ord(self._source[self._index])

        while cc in [32, 10, 9, 13]:
            self._index += 1
            if self._length <= self._index:
                return
            cc = ord(self._source[self._index])

    def getIdentifier(self):
        index = self._index
        start = index
        source = self._source
        cc = ord(source[start])

        while (cc >= 95 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
              cc == 95:
            index += 1
            cc = ord(source[index])

        self._index = index

        return {
            'type': 'Identifier',
            'name': source[start:index]
        }

    def getEntity(self, id, index):
        if not self.getRequiredWS():
            raise Exception("Foo")
        
        ch = self._source[self._index]
        value = self.getValue(True, ch)
        attrs = []
        if value is None:
            if ch == '>':
                raise Exception()
            attrs = self.getAttributes()
        else:
            ws1 = self.getRequiredWS()
            if not self._source[self._index] == '>':
                if not ws1:
                    raise Exception()
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
        cc = self._source[self._index]

        if cc == '<':
            self._index += 1
            id = self.getIdentifier()
            cc = self._source[self._index]

            if cc == '(':
                return self.getMacro()
            if cc == '[':
                self._index += 1
                return self.getEntity(id,
                                      self.getItemList(self.getExpression, ']'))
            return self.getEntity(id, [])

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
