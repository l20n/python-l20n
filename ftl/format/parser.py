
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

    def getIdentifierWithSpace(nsSep = None):
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
            quoteDelimited = true
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

class FTLParser():
  def parseResource(self, string):
    parseContext = ParseContext(string)
    return parseContext.getResource()
