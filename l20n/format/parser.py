
from . import ast


class L10nError(Exception):
    def __init__(self, message, pos=None, context=None):
        self.name = 'L10nError'
        self.message = message
        self.pos = pos
        self.context = context

MAX_PLACEABLES = 100


class ParseContext():
    def __init__(self, string, with_source=True):
        self._source = string
        self._index = 0
        self._length = len(string)

        self._lastGoodEntryEnd = 0

        self.with_source = with_source

    def _isIdentifierStart(self, cc):
        return (cc >= 97 and cc <= 122) or \
               (cc >= 65 and cc <= 90) or \
                cc == 95

    def _getch(self, pos=None, offset=0):
        if pos is None:
            pos = self._index
        if pos + offset >= self._length:
            return ''
        return self._source[pos + offset]

    def _getcc(self, pos=None, offset=0):
        if pos is None:
            pos = self._index
        if pos + offset >= self._length:
            return -1
        return ord(self._source[pos + offset])

    def getResource(self):
        resource = ast.Resource()
        errors = []
        comment = None

        section = resource.body

        if self._getch() == '#':
            comment = self.getComment()

            cc = self._getcc()
            if not self._isIdentifierStart(cc):
                resource.comment = comment
                comment = None

        self.getWS()

        while self._index < self._length:
            try:
                entry = self.getEntry(comment)

                if isinstance(entry, ast.Section):
                    resource.body.append(entry)
                    section = entry.body
                else:
                    section.append(entry)
                self._lastGoodEntryEnd = self._index
                comment = None
            except L10nError as e:
                errors.append(e)
                section.append(self.getJunkEntry())

            self.getWS()

        return [resource, errors]

    def getEntry(self, comment=None):
        if self._index is not 0 and \
                self._source[self._index - 1] != '\n':
            raise self.error('Expected new line and a new entry')

        if comment is None and self._getch() == '#':
            comment = self.getComment()

        self.getLineWS()

        if self._getch() == '[':
            return self.getSection(comment)

        if self._index < self._length and \
                self._getch() != '\n':
            return self.getEntity(comment)

        return comment

    def getSection(self, comment=None):
        self._index += 1
        if self._getch() != '[':
            raise self.error('Expected "[[" to open a section')

        self._index += 1

        self.getLineWS()

        key = self.getKeyword()

        self.getLineWS()

        if self._getch() != ']' or \
           self._getch(None, 1) != ']':
            raise self.error('Expected "]]" to close a section')

        self._index += 2

        return ast.Section(key, [], comment)

    def getEntity(self, comment=None):
        id = self.getIdentifier()

        members = []
        value = None

        self.getLineWS()

        ch = self._getch()

        if ch != '=':
            raise self.error('Expected "=" after Entity ID')

        self._index += 1
        ch = self._getch()

        self.getLineWS()

        value = self.getPattern()

        ch = self._getch()

        if ch == '\n':
            self._index += 1
            self.getLineWS()
            ch = self._getch()

        if (ch == '[' and self._source[self._index + 1] != '[') or \
                ch == '*':
            members = self.getMembers()
        elif value is None:
            raise self.error('Expected a value (like: " = value") or a ' +
                             'trait (like: "[key] value")')

        return ast.Entity(id, value, members, comment)

    def getWS(self):
        cc = self._getcc()

        while cc == 32 or cc == 10 or cc == 0 or cc == 13:
            self._index += 1
            cc = self._getcc()

    def getLineWS(self):
        cc = self._getcc()

        while cc == 32 or cc == 9:
            self._index += 1
            cc = self._getcc()

    def getIdentifier(self):
        name = ''

        start = self._index
        cc = self._getcc()

        if self._isIdentifierStart(cc):
            self._index += 1
            cc = self._getcc()
        elif len(name) == 0:
            raise self.error(
                'Expected an identifier (starting with [a-zA-Z_])')

        while (cc >= 97 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
                cc == 95 or cc == 45:
            self._index += 1
            cc = self._getcc()

        name += self._source[start:self._index]
        return ast.Identifier(name)

    def getKeyword(self):
        name = ''
        namespace = self.getIdentifier().name

        if self._getch() == '/':
            self._index += 1
        elif namespace:
            name = namespace
            namespace = None

        start = self._index
        cc = self._getcc()

        if self._isIdentifierStart(cc):
            self._index += 1
            cc = self._getcc()
        elif len(name) == 0:
            raise self.error(
                'Expected an identifier (starting with [a-zA-Z_])')

        while (cc >= 97 and cc <= 122) or \
                (cc >= 65 and cc <= 90) or \
                (cc >= 48 and cc <= 57) or \
                cc == 95 or cc == 45 or cc == 32:
            self._index += 1
            cc = self._getcc()

        while self._getcc(offset=-1) == 32:
            self._index -= 1

        name += self._source[start:self._index]
        return ast.Keyword(name, namespace)

    def getPattern(self):
        buffer = ''
        source = ''
        content = []
        quoteDelimited = None
        firstLine = True

        ch = self._getch()

        if ch == '\\':
            ch2 = self._getch(None, 1)
            if ch2 == '"' or ch2 == '{' or ch2 == '\\':
                self._index += 1
                buffer += self._getch()
                self._index += 1
                ch = self._getch()
        elif ch == '"':
            quoteDelimited = True
            self._index += 1
            ch = self._getch()

        while self._index < self._length:
            if ch == '\n':
                if quoteDelimited:
                    raise self.error('Unclosed string')
                self._index += 1
                self.getLineWS()
                if self._getch() != '|':
                    break
                if firstLine and len(buffer):
                    raise self.error('Multiline string should have the ID ' +
                                     'empty')
                firstLine = False
                self._index += 1
                if self._getch() == ' ':
                    self._index += 1
                if len(buffer):
                    buffer += '\n'
                ch = self._getch()
                continue
            elif ch == '\\':
                ch2 = self._getch(None, 1)
                if (quoteDelimited and ch2 == '"') or ch2 == '{':
                    ch = ch2
                    self._index += 1
            elif quoteDelimited and ch == '"':
                self._index += 1
                quoteDelimited = False
                break
            elif ch == '{':
                if len(buffer):
                    content.append(ast.TextElement(buffer))
                source += buffer
                buffer = ''
                start = self._index
                content.append(self.getPlaceable())
                source += self._source[start:self._index]
                ch = self._getch()
                continue

            if ch:
                buffer += ch
            self._index += 1
            ch = self._getch()

        if quoteDelimited:
            raise self.error('Unclosed string')

        if len(buffer):
            source += buffer
            content.append(ast.TextElement(buffer))

        if len(content) == 0:
            if quoteDelimited is not None:
                content.append(ast.TextElement(source))
            else:
                return None

        return ast.Pattern(
            source=source if self.with_source else None,
            elements=content,
            quoted=quoteDelimited is not None
        )

    def getPlaceable(self):
        self._index += 1

        expressions = []

        self.getLineWS()

        while self._index < self._length:
            start = self._index
            try:
                expressions.append(self.getPlaceableExpression())
            except L10nError as e:
                raise self.error(e.description, start)
            self.getWS()
            if self._getch() == '}':
                self._index += 1
                break
            elif self._getch() == ',':
                self._index += 1
                self.getWS()
            else:
                raise self.error('Exepected "}" or ","')

        return ast.Placeable(expressions)

    def getPlaceableExpression(self):
        selector = self.getCallExpression()
        members = None

        self.getWS()

        if self._getch() != '}' and \
           self._getch() != ',':
            if self._getch() != '-' or \
               self._getch(None, 1) != '>':
                raise self.error('Expected "}", "," or "->"')
            self._index += 2

            self.getLineWS()

            if self._getch() != '\n':
                raise self.error('Members should be listed in a new line')

            self.getWS()

            members = self.getMembers()

            if len(members) == 0:
                raise self.error('Expected members for the select expression')

        if members is None:
            return selector

        return ast.SelectExpression(selector, members)

    def getCallExpression(self):
        exp = self.getMemberExpression()

        if self._getch() != '(':
            return exp

        self._index += 1

        args = self.getCallArgs()

        self._index += 1

        if isinstance(exp, ast.EntityReference):
            exp = ast.FunctionReference(exp.name)

        return ast.CallExpression(exp, args)

    def getCallArgs(self):
        args = []

        if self._getch() == ')':
            return args

        while self._index < self._length:
            self.getLineWS()

            exp = self.getCallExpression()

            if not isinstance(exp, ast.EntityReference):
                args.append(exp)
            else:
                self.getLineWS()

                if self._getch() == ':':
                    self._index += 1
                    self.getLineWS()

                    val = self.getCallExpression()

                    if isinstance(val, ast.EntityReference) or \
                       isinstance(val, ast.MemberExpression):
                        self._index = \
                                self._source.rfind('=', 0, self._index) + 1
                        raise self.error('Expected string in quotes')

                    args.append(ast.KeyValueArg(exp.name, val))
                else:
                    args.append(exp)

            self.getLineWS()

            if self._getch() == ')':
                break
            elif self._getch() == ',':
                self._index += 1
            else:
                raise self.error('Expected "," or ")"')

        return args

    def getNumber(self):
        num = ''
        cc = self._getcc()

        if cc == 45:
            num += '-'
            self._index += 1
            cc = self._getcc()

        if cc < 48 or cc > 57:
            raise self.error('Unknown literal "' + num + '"')

        while cc >= 48 and cc <= 57:
            num += self._source[self._index]
            self._index += 1
            cc = self._getcc()

        if cc == 46:
            num += self._getch()
            self._index += 1
            cc = self._getcc()

            if cc < 48 or cc > 57:
                raise self.error('Unknown literal "' + num + '"')

            while cc >= 48 and cc <= 57:
                num += self._source[self._index]
                self._index += 1
                cc = self._getcc()

        return ast.Number(num)

    def getMemberExpression(self):
        exp = self.getLiteral()

        while self._getch() == '[':
            keyword = self.getMemberKey()
            exp = ast.MemberExpression(exp, keyword)

        return exp

    def getMembers(self):
        members = []

        while self._index < self._length:
            if (self._getch() != '[' or
                self._getch(None, 1) == '[') and \
               self._getch() != '*':
                break

            default = False

            if self._getch() == '*':
                self._index += 1
                default = True

            if self._getch() != '[':
                raise self.error('Expected "["')

            key = self.getMemberKey()

            self.getLineWS()

            value = self.getPattern()

            member = ast.Member(key, value, default)

            members.append(member)

            self.getWS()

        return members

    def getMemberKey(self):
        self._index += 1

        cc = self._getcc()
        literal = None

        if (cc >= 48 and cc <= 57) or cc == 45:
            literal = self.getNumber()
        else:
            literal = self.getKeyword()

        if self._getch() != ']':
            raise self.error('Expected "]"')

        self._index += 1
        return literal

    def getLiteral(self):
        cc = self._getcc()
        if (cc >= 48 and cc <= 57) or cc == 45:
            return self.getNumber()
        elif cc == 34:
            return self.getPattern()
        elif cc == 36:
            self._index += 1
            name = self.getIdentifier().name
            return ast.ExternalArgument(name)

        name = self.getIdentifier().name
        return ast.EntityReference(name)

    def getComment(self):
        self._index += 1
        if self._getch() == ' ':
            self._index += 1

        content = ''

        eol = self._source.find('\n', self._index)

        content += self._source[self._index:eol]

        while eol != -1 and self._getch(eol + 1) == '#':
            self._index = eol + 2

            if self._getch() == ' ':
                self._index += 1

            eol = self._source.find('\n', self._index)

            if eol == -1:
                break

            content += '\n' + self._source[self._index:eol]

        if eol == -1:
            self._index = self._length
        else:
            self._index = eol + 1

        return ast.Comment(content)

    def error(self, message, start=None):
        pos = self._index

        if start is None:
            start = pos

        start = self._findEntityStart(start)

        context = self._source[start: pos + 10]

        msg = '\n\n ' + message + '\nat pos ' + str(pos) + \
            ':\n------\n...' + context + '\n------'
        err = L10nError(msg)

        # row = len(self._source[0:pos].split('\n'))
        # col = pos - self._source.rfind('\n', 0, pos - 1)
        # err._pos = {start: pos, end: None, col: col, row: row}
        err.offset = pos - start
        err.description = message
        err.context = context
        return err

    def getJunkEntry(self):
        pos = self._index

        nextEntity = self._findNextEntryStart(pos)

        if nextEntity == -1:
            nextEntity = self._length

        self._index = nextEntity

        entityStart = self._findEntityStart(pos)

        if entityStart < self._lastGoodEntryEnd:
            entityStart = self._lastGoodEntryEnd

        junk = ast.JunkEntry(self._source[entityStart:nextEntity])
        return junk

    def _findEntityStart(self, pos):
        start = pos

        while True:
            end = start - 2
            if end < 0:
                end = 0
            start = self._source.rfind('\n', 0, end)
            if start == -1 or start == 0:
                start = 0
                break

            cc = self._getcc(start + 1)

            if self._isIdentifierStart(cc):
                start += 1
                break

        return start

    def _findNextEntryStart(self, pos):
        start = pos

        while True:
            if start == 0 or self._getch(start - 1) == '\n':
                cc = self._getcc(start)

                if self._isIdentifierStart(cc) or cc == 35 or cc == 91:
                    break

            start = self._source.find('\n', start)

            if start == -1:
                break
            start += 1

        return start


class FTLParser():
    def parse(self, string, with_source=True):
        parseContext = ParseContext(string, with_source)
        return parseContext.getResource()

    def parseResource(self, string, with_source=True):
        parseContext = ParseContext(string, with_source)
        [ast, errors] = parseContext.getResource()
        return [ast.toJSON(), errors]
