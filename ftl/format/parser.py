
from . import ast

class L10nError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'L10nError'
        self.message = message
        self.pos = pos
        self.context = context

MAX_PLACEABLES = 100


class ParseContext():
    def __init__(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        self._lastGoodEntryEnd = 0

    def _getch(self, offset = 0):
        if self._index + offset >= self._length:
            return ''
        return self._source[self._index + offset]

    def _getcc(self, offset = 0):
        if self._index + offset >= self._length:
            return -1
        return ord(self._source[self._index + offset])

    def getResource(self):
        resource = ast.Resource()
        resource._errors = []

        self.getWS()

        while self._index < self._length:
            try:
                resource.body.append(self.getEntry())
            except L10nError:
                resource._errors.append(e)
                resource.body.append(self.getJunkEntry())

            self.getWS()

        return resource

    def getEntry(self):
        if (self._index is not 0 and \
            self._source[self._index - 1] != '\n'):
            raise self.error('Expected new line and a new entry')

        comment = None

        if self._source[self._index] == '#':
            comment = self.getComment()

        self.getLineWS()

        if self._source[self._index] == '[':
            return self.getSection(comment)

        if self._index < self._length and \
          self._source[self._index] is not '\n':
              return self.getEntity(comment)

        return comment

    def getSection(self, comment = None):
        self._index += 1
        if self._getch() != '[':
            raise self.error('Expected "[[" to open a section')

        self._index += 1

        self.getLineWS()

        id = self.getIdentifier()

        self.getLineWS()

        if self._getch() != ']' or \
           self._getch(1) != ']':
            raise self.error('Expected "]]" to close a section')

        self._index += 2

        return ast.Section(id, comment)

    def getEntity(self, comment = None):
        id = self.getIdentifier('/')

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

        if ((ch == '[' and self._source[self._index + 1] != '[') or \
            ch == '*'):
            members = self.getMembers()
        elif value is None:
            raise self.error()

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

    def getIdentifier(self, nsSep = None):
        namespace = None
        id = ''

        if nsSep:
            namespace = self.getIdentifier().name
            if self._getch() == nsSep:
                self._index += 1
            elif namespace:
                id = namespace
                namespace = None

        start = self._index
        cc = self._getcc()

        if (cc >= 97 and cc <= 122) or \
           (cc >= 65 and cc <= 90) or \
           (cc >= 48 and cc <= 57) or \
           cc == 95 or cc == 45:
            self._index += 1
            cc = self._getcc()
        elif len(id) == 0:
            raise self.error('Expected an identifier (starting with [a-zA-Z_])')


        while (cc >= 97 and cc <= 122) or \
              (cc >= 65 and cc <= 90) or \
              (cc >= 48 and cc <= 57) or \
               cc == 95 or cc == 45:
            self._index += 1
            cc = self._getcc()

        id += self._source[start:self._index]
        return ast.Identifier(id, namespace)

    def getIdentifierWithSpace(self, nsSep = None):
        namespace = None
        id = ''

        if nsSep:
            namespace = self.getIdentifier().name
            if self._getch() == nsSep:
                self._index += 1
            elif namespace:
                id = namespace
                namespace = None

        start = self._index
        cc = self._getcc()

        if (cc >= 97 and cc <= 122) or \
           (cc >= 65 and cc <= 90) or \
           (cc >= 48 and cc <= 57) or \
           cc == 95 or cc == 45:
            self._index += 1
            cc = self._getcc()

        id += self._source[start:self._index]
        return ast.Identifier(id, namespace)

    def getPattern(self):
        buffer = ''
        source = ''
        content = []
        quoteDelimited = None
        firstLine = True

        ch = self._getch()

        if ch == '\\':
            ch2 = self._getch(1)
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
                    raise self.error()
                self._index += 1
                self.getLineWS()
                if self._getch() != '|':
                    break;
                if firstLine and len(buffer):
                    raise self.error()
                firstLine = False
                self._index += 1
                if self._getch() == ' ':
                    self._index += 1
                if len(buffer):
                    buffer += '\n'
                ch = self._getch()
                continue
            elif ch == '\\':
                ch2 = self._getch(1)
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

        pattern = ast.Pattern(source, content)
        pattern._quoteDelim = quoteDelimited is not None
        return pattern

    def getPlaceable(self):
        self._index += 1

        expressions = []

        self.getLineWS()

        while self._index < self._length:
            start = self._index
            try:
                expressions.append(self.getPlaceableExpression())
            except L10nError, e:
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
               self._getch(1) != '>':
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
            return selector;

        return ast.SelectExpression(selector, members)

    def getCallExpression(self):
        exp = self.getMemberExpression()

        if self._getch() != '(':
            return exp

        self._index += 1

        args = self.getCallArgs()

        self._index += 1

        if isinstance(exp, ast.EntityReference):
            exp = ast.BuiltinReference(exp.name, exp.namespace)

        return ast.CallExpression(exp, args)

    def getCallArgs(self):
        args = []

        if self._getch() == ')':
            return args

        while self._index < self._length:
            self.getLineWS()

            exp = self.getCallExpression()

            if isinstance(exp, ast.EntityReference) or \
               exp.namespace is not None:
                args.append(exp)
            else:
                self.getLineWS()

                if self._getch() == ':':
                    self._index += 1
                    self.getLineWS()

                    val = self.getCallExpression()

                    if isinstance(val, ast.EntityReference) or \
                       isinstance(val, ast.MemberExpression):
                        self._index = self._source.rfind('=', self._index) + 1
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

    def getNumber():
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
            keyword = self.getKeyword()
            exp = ast.MemberExpression(exp, keyword)

        return exp

    def getMembers(self):
        members = []

        while self._index < self._length:
            if (self._getch() != '[' or \
                self._getch(1) == '[') and \
               self._getch() != '*':
                break
            
            default = False

            if self._getch() == '*':
                self._index += 1
                default = True

            if self._getch() != '[':
                raise self.error('Expected "["')

            key = self.getKeyword()

            self.getLineWS()

            value = self.getPattern()

            member = ast.Member(key, value, default)

            members.append(member)

            self.getWS()

        return members

    def getKeyword(self):
        self._index += 1

        cc = self._getcc()
        literal = None

        if (cc >= 48 and cc <= 57) or cc == 45:
            literal = self.getNumber()
        else:
            literal = self.getIdentifierWithSpace('/')

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
            id = self.getIdentifier()
            return ast.ExternalArgument(id.name)

        id = self.getIdentifier('/')
        return ast.EntityReference(id.name, id.namespace)

    def getComment(self):
        self._index += 1
        if self._getch() == ' ':
            self._index += 1

        content = ''

        eol = self._source.find('\n', self._index)

        content += self._source[self._index:eol]

        while eol != -1 and self._source[eol + 1] == '#':
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

    def error(message, start = None):
        print(message)
        err = L10nError()
        return err


class FTLParser():
  def parseResource(self, string):
    parseContext = ParseContext(string)
    return parseContext.getResource()
