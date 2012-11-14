#!/usr/bin/python 
import re
import os
import codecs
import l20n.format.lol.ast as ast
import l20n.format.lol.serializer as serializer

def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

def write_file(path, s):
    f = codecs.open(path, encoding='utf_8', mode='w+')
    f.write(s)
    f.close()

class PropertiesConverter:
    patterns = {
        'entity': re.compile('([^=]+)=(.+)'),
        'locale': re.compile('\[([a-zA-Z\-]+)\]'),
        'comment': re.compile('#(.*)')
    }

    def __init__(self, s, locale=None):
        self.s = s.split('\n')
        self.lols = {}
        self._current_locale = locale
        if locale:
            self.lols[locale] = ast.LOL()

    def parse(self):
        for line in self.s:
            self.get_token(line)
        return self.lols

    def get_token(self, line):
        s = line.strip()
        if len(s) == 0:
            return
        if s[0] == '[':
            locale = self.get_locale(s)
            return locale
        if s[0] == '#':
            return self.get_comment(s)
        return self.get_entity(s)

       
    def get_locale(self, line):
        m = self.patterns['locale'].match(line)
        if m:
            locale = m.group(1)
            self.lols[locale] = ast.LOL()
            self._current_locale = locale
            #print('locale: %s' % locale)

    def get_comment(self, line):
        m = self.patterns['comment'].match(line)
        if m:
            comment = m.group(1)
            #print('comment: %s' % comment)
            c = ast.Comment(comment)
            self.lols[self._current_locale].body.append(c)

    def get_entity(self, line):
        m = self.patterns['entity'].match(line)
        if m:
            id = m.group(1).replace('-', '_')
            val = m.group(2)
            #print("entity %s = %s" % (id, val))
            id = ast.Identifier(id)
            entity = ast.Entity(id)
            entity.value = ast.String(val)
            self.lols[self._current_locale].body.append(entity)


def convert(paths, app, source_locale):
    locales_path = os.path.join(paths['gaia'], 'apps', app, 'locales')
    source_locale_path = os.path.join(locales_path, '%s.%s.properties' % (app, source_locale))

    f = read_file(source_locale_path)
    pc = PropertiesConverter(f, locale='en-US')
    lols = pc.parse()
    ser = serializer.Serializer()
    for (loc, lol) in lols.items():
        s = ser.serialize(lol)
        write_file(os.path.join(locales_path, '%s.%s.lol' % (app, loc)), s)

if __name__ == '__main__':
    paths = {
        'gaia': '/Users/zbraniecki/projects/gaia',
    }
    app = 'browser'
    source_locale = 'en-US'
    convert(paths, app, source_locale)

