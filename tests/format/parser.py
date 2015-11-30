import unittest
import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, '..', '..'))

from l20n.format.parser import L20nParser


class L20nParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = L20nParser()

    def test_string_value(self):
        string = "<id 'string'>"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        self.assertEqual(resource.body[0].id.name, "id")
        self.assertEqual(resource.body[0].value.source, 'string')
        self.assertEqual(resource.body[0].value.content[0], 'string')

        string = '<id "string">'
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        self.assertEqual(resource.body[0].id.name, "id")
        self.assertEqual(resource.body[0].value.source, 'string')
        self.assertEqual(resource.body[0].value.content[0], 'string')

#        string = "<id '''string'''>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        self.assertEqual(resource.body[0].id.name, "id")
#        self.assertEqual(resource.body[0].value.source, 'string')

#        string = '<id """string""">'
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        self.assertEqual(resource.body[0].id.name['name'], "id")
#        self.assertEqual(resource.body[0].value.source, 'string')

    def test_string_value_quotes(self):
        string = '<id "str\\"ing">'
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.source, 'str\\"ing')
        self.assertEqual(resource.body[0].value.content[0], 'str"ing')

        string = "<id 'str\\'ing'> "
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.source, "str\\'ing")
        self.assertEqual(resource.body[0].value.content[0], 'str\'ing')

#        string = '<id """str"ing""">'
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0].value.source, 'str"ing')

#        string = "<id '''str'ing'''>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0].value.source, "str'ing")

#        string = '<id """"string\\"""">'
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0].value.source, '"string"')

#        string = "<id ''''string\\''''>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0].value.source, "'string'")

        string = "<id 'test \{{ more'>"
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.source, "test \\{{ more")

        string = "<id 'test \\\\ more'>"
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.source, "test \\\\ more")

    def test_string_unicode(self):
        string = u"<id 'foo \\u00bd = \u00bd'>"
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.source, u"foo \\u00bd = \u00bd")
    def test_basic_errors(self):
        strings = [
            '< "str\\"ing">',
            "<>",
            "<id",
            "<id ",
            "id>",
            '<id "value>',
            '<id value">',
            "<id 'value>",
            "<id value'",
            "<id'value'>",
            '<id"value">',
            '<id """value"""">',
            '< id "value">',
            '<()>',
            '<+s>',
            '<id-id2>',
            '<-id>',
            '<id 2>',
            '<"id">',
            '<\'id\'>',
            '<2>',
            '<09>',
        ]
        for string in strings:
            resource = self.parser.parse('<pre "value">' +
                                         string +
                                         '<post "VALUE">')
            self.assertEqual(len(resource._errors), 1)
            self.assertEqual(resource.body[0].value.content[0], 'value')
            self.assertEqual(resource.body[0].id.name, 'pre')
            self.assertEqual(resource.body[2].value.content[0], 'VALUE')
            self.assertEqual(resource.body[2].id.name, 'post')

    def test_complex_strings(self):
        string = "<id 'test {{ id }} test2'>"
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.content[0], 'test ')
        self.assertEqual(resource.body[0].value.content[1].name, 'id')
        self.assertEqual(resource.body[0].value.content[2], ' test2')

    def test_basic_attributes(self):
        string = "<id attr1: 'foo'>"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body[0].attrs), 1)
        attr = resource.body[0].attrs[0]
        self.assertEqual(attr.value.source, "foo")

        string = "<id attr1: 'foo' attr2: 'foo2'    >"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body[0].attrs), 2)
        attr = resource.body[0].attrs[0]
        self.assertEqual(attr.value.source, "foo")

        string = "<id 'value' attr1: 'foo' attr2: 'foo2' attr3: 'foo3' >"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body[0].attrs), 3)
        self.assertEqual(resource.body[0].value.source, 'value')
        attr = resource.body[0].attrs[0]
        self.assertEqual(attr.value.source, "foo")
        attr = resource.body[0].attrs[1]
        self.assertEqual(attr.value.source, "foo2")
        attr = resource.body[0].attrs[2]
        self.assertEqual(attr.value.source, "foo3")

#    def test_attributes_with_indexes(self):
#        string = "<id attr[2]: 'foo'>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0]['attr']['x'], 2)
#        string = "<id attr[2+3?'foo':'foo2']: 'foo'>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual((resource.body[0]['attrs'][0]['index'][0]['test']
#                          ['left'].value.source), 2)
#        self.assertEqual((resource.body[0]['attrs'][0]['index'][0]['test']
#                          ['right'].value.source), 3)
#        string = "<id attr[2, 3]: 'foo'>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0]['attrs'][0]['index'][0].value.source, 2)
#        self.assertEqual(resource.body[0]['attrs'][0]['index'][1].value.source, 3)

    def test_attribute_errors(self):
        strings = [
            '<id : "foo">',
            "<id 2: >",
            "<id a: >",
            "<id: ''>",
            "<id a: b:>",
            "<id a: 'foo' 'heh'>",
            "<id a: 2>",
            "<id 'a': 'a'>",
            "<id \"a\": 'a'>",
            "<id 2: 'a'>",
            "<id a2:'a'a3:'v'>",
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)


    def test_hash_value(self):
        string = "<id {*a: 'b', a2: 'c', d: 'd' }>"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        val = resource.body[0].value
        self.assertEqual(len(val.items), 3)
        self.assertEqual(val.items[0].value.source, 'b')

        string = "<id {*a: '2', b: '3'} >"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        val = resource.body[0].value
        self.assertEqual(len(val.items), 2)
        self.assertEqual(val.items[0].value.source, '2')
        self.assertEqual(val.items[1].value.source, '3')

    def test_hash_value_with_trailing_comma(self):
        string = "<id {*a: '2', b: '3', } >"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        val = resource.body[0].value
        self.assertEqual(len(val.items), 2)
        self.assertEqual(val.items[0].value.source, '2')
        self.assertEqual(val.items[1].value.source, '3')

    def test_nested_hash_value(self):
        string = "<id {*a: 'foo', b: {*a2: 'p'}}>"
        resource = self.parser.parse(string)
        self.assertEqual(len(resource.body), 1)
        val = resource.body[0].value
        self.assertEqual(len(val.items), 2)
        self.assertEqual(val.items[0].value.source, 'foo')
        self.assertEqual(val.items[1].value.items[0].value.source, 'p')

    def test_hash_with_default(self):
        string = "<id {a: 'v', *b: 'c'}>"
        resource = self.parser.parse(string)
        self.assertEqual(resource.body[0].value.items[1].default, True)

    def test_hash_errors(self):
        strings = [
            '<id {}>',
            '<id {a: 2}>',
            "<id {a: 'd'>",
            "<id a: 'd'}>",
            "<id {{a: 'd'}>",
            "<id {a: 'd'}}>",
            "<id {a:} 'd'}>",
            "<id {2}>",
            "<id {'a': 'foo'}>",
            "<id {\"a\": 'foo'}>",
            "<id {2: 'foo'}>",
            "<id {a:'foo'b:'foo'}>",
            "<id {a }>",
            '<id {a: 2, b , c: 3 } >',
            '<id {a: 2, b: 3}>',
            '<id {*a: {d: 3}, b: 3}>',
#           '<id {*a: "v", *b: "c"}>',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_index(self):
#        string = "<id[]>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        self.assertEqual(len(resource.body[0]['index']), 0)
#        self.assertEqual(resource.body[0].value.source, None)

#        #string = "<id[ ] >"
#        #resource.body = self.parser.parse(string)
#        #self.assertEqual(len(resource.body), 1)
#        #self.assertEqual(len(resource.body[0]['index']), 0)
#        #self.assertEqual(resource.body[0].value.source, None)
#
#        string = "<id['foo'] 'foo2'>"
#        resource.body = self.parser.parse(string)
#        entity = resource.body[0]
#        self.assertEqual(entity['index'][0], "foo")
#        self.assertEqual(entity.value.source, "foo2")
#
#        string = "<id[2] 'foo2'>"
#        resource.body = self.parser.parse(string)
#        entity = resource.body[0]
#        self.assertEqual(entity['index'][0].value.source, 2)
#        self.assertEqual(entity.value.source, "foo2")
#
#        string = "<id[2, 'foo', 3] 'foo2'>"
#        resource.body = self.parser.parse(string)
#        entity = resource.body[0]
#        self.assertEqual(entity['index'][0].value.source, 2)
#        self.assertEqual(entity['index'][1], 'foo')
#        self.assertEqual(entity['index'][2].value.source, 3)
#        self.assertEqual(entity.value.source, "foo2")
#
    def test_index_errors(self):
        strings = [
            '<id[ "foo">',
            '<id] "foo">',
            '<id[ \'] "foo">',
            '<id{ ] "foo">',
            '<id[ } "foo">',
            '<id[" ] "["a"]>',
            '<id[a]["a"]>',
            '<id["foo""foo"] "fo">',
            '<id[a, b, ] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_macro(self):
#        string = "<id($n) {2}>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        self.assertEqual(len(resource.body[0]['args']), 1)
#        self.assertEqual(resource.body[0]['expression'].value.source, 2)
#
#        string = "<id( $n, $m, $a ) {2}  >"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        self.assertEqual(len(resource.body[0]['args']), 3)
#        self.assertEqual(resource.body[0]['expression'].value.source, 2)
#
    def test_macro_errors(self):
        strings = [
            '<id (n) {2}>',
            '<id ($n) {2}>',
            '<(n) {2}>',
            '<id(() {2}>',
            '<id()) {2}>',
            '<id[) {2}>',
            '<id(] {2}>',
            '<id(-) {2}>',
            '<id(2+2) {2}>',
            '<id("a") {2}>',
            '<id(\'a\') {2}>',
            '<id(2) {2}>',
            '<_id($n) {2}>',
            '<id($n) 2}>',
            '<id($n',
            '<id($n ',
            '<id($n)',
            '<id($n) ',
            '<id($n) {',
            '<id($n) { ',
            '<id($n) {2',
            '<id($n) {2}',
            '<id(nm nm) {2}>',
            '<id($n) {}>',
            '<id($n, $m ,) {2}>',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_expression(self):
#        string = "<id[0 == 1 || 1] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['left']['operator']['token'], '==')
#
#        string = "<id[a == b == c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '==')
#        self.assertEqual(exp['left']['operator']['token'], '==')
#
#        string = "<id[ a == b || c == d || e == f ] 'foo'  >"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['left']['operator']['token'], '||')
#        self.assertEqual(exp['right']['operator']['token'], '==')
#
#        string = "<id[0 && 1 || 1] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['left']['operator']['token'], '&&')
#
#        string = "<id[0 && (1 || 1)] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '&&')
#        self.assertEqual(exp['right']['expression']['operator']['token'], '||')
#
#        string = "<id[1 || 1 && 0] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['right']['operator']['token'], '&&')
#
#        string = "<id[1 + 2] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '+')
#        self.assertEqual(exp['left'].value.source, 1)
#        self.assertEqual(exp['right'].value.source, 2)
#
#        string = "<id[1 + 2 - 3 > 4 < 5 <= a >= 'd' * 3 / q % 10] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '>=')
#
#        string = "<id[! +1] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '!')
#        self.assertEqual(exp['argument']['operator']['token'], '+')
#        self.assertEqual(exp['argument']['argument'].value.source, 1)
#
#        string = "<id[1+2] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '+')
#        self.assertEqual(exp['left'].value.source, 1)
#        self.assertEqual(exp['right'].value.source, 2)
#
#        string = "<id[(1+2)] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]['expression']
#        self.assertEqual(exp['operator']['token'], '+')
#        self.assertEqual(exp['left'].value.source, 1)
#        self.assertEqual(exp['right'].value.source, 2)
#
#        string = "<id[id2['foo']] 'foo2'>"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(len(resource.body), 1)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(resource.body[0].value.source, 'foo2')
#        self.assertEqual(exp['expression']['name'], 'id2')
#        self.assertEqual(exp['property'], 'foo')
#
#        #string = "<id[id['foo']]>"
#        #resource.body = self.parser.parse(string)
#        #self.assertEqual(len(resource.body), 1)
#        #exp = resource.body[0]['index'][0]
#        #self.assertEqual(resource.body[0].value.source, None)
#        #self.assertEqual(exp['expression']['name'], 'id')
#        #self.assertEqual(exp['property'] , 'foo')
#
    def test_expression_errors(self):
        strings = [
            '<id[1+()] "foo">',
            '<id[1<>2] "foo">',
            '<id[1+=2] "foo">',
            '<id[>2] "foo">',
            '<id[1==] "foo">',
            '<id[1+ "foo">',
            '<id[2==1+] "foo">',
            '<id[2==3+4 "fpp">',
            '<id[2==3+ "foo">',
            '<id[2>>2] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_logical_expression(self):
#        string = "<id[0 || 1] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['left'].value.source, 0)
#        self.assertEqual(exp['right'].value.source, 1)
#
#        string = "<id[0 || 1 && 2 || 3] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['left']['operator']['token'], '||')
#        self.assertEqual(exp['right'].value.source, 3)
#        self.assertEqual(exp['left']['left'].value.source, 0)
#        self.assertEqual(exp['left']['right']['left'].value.source, 1)
#        self.assertEqual(exp['left']['right']['right'].value.source, 2)
#        self.assertEqual(exp['left']['right']['operator']['token'], '&&')
#
#    def test_logical_expression_errors(self):
#        strings = [
#            '<id[0 || && 1] "foo">',
#            '<id[0 | 1] "foo">',
#            '<id[0 & 1] "foo">',
#            '<id[|| 1] "foo">',
#            '<id[0 ||] "foo">',
#        ]
#        for string in strings:
#            try:
#                self.assertRaises(ParserError, self.parser.parse, string)
#            except AssertionError:
#                raise AssertionError("Failed to raise parser error on: " +
#                                     string)
#
#    def test_binary_expression(self):
#        #from pudb import set_trace; set_trace()
#        string = "<id[a / b * c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '*')
#        self.assertEqual(exp['left']['operator']['token'], '/')
#
#        string = "<id[8 * 9 % 11] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '%')
#        self.assertEqual(exp['left']['operator']['token'], '*')
#
#        string = "<id[6 + 7 - 8 * 9 / 10 % 11] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '-')
#        self.assertEqual(exp['left']['operator']['token'], '+')
#        self.assertEqual(exp['right']['operator']['token'], '%')
#
#        string = ("<id[0 == 1 != 2 > 3 < 4 >= 5 <= 6 + 7 - 8 * 9 / 10 % 11]"
#                  " 'foo'>")
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '!=')
#        self.assertEqual(exp['left']['operator']['token'], '==')
#        self.assertEqual(exp['right']['operator']['token'], '<=')
#        self.assertEqual(exp['right']['left']['operator']['token'], '>=')
#        self.assertEqual(exp['right']['right']['operator']['token'], '-')
#        self.assertEqual(exp['right']['left']['left']['operator']['token'],
#                         '<')
#        self.assertEqual(exp['right']['left']['right'].value.source, 5)
#        self.assertEqual((exp['right']['left']['left']['left']
#                          ['operator']['token']), '>')
#        self.assertEqual(exp['right']['right']['left']['operator']['token'],
#                         '+')
#        self.assertEqual(exp['right']['right']['right']['operator']['token'],
#                         '%')
#        self.assertEqual((exp['right']['right']['right']['left']
#                          ['operator']['token']), '*')
#        self.assertEqual((exp['right']['right']['right']['left']['right']
#                          ['operator']['token']), '/')
#
#    def test_binary_expression_errors(self):
#        strings = [
#            '<id[1 \ 2] "foo">',
#            '<id[1 ** 2] "foo">',
#            '<id[1 * / 2] "foo">',
#            '<id[1 !> 2] "foo">',
#            '<id[1 <* 2] "foo">',
#            '<id[1 += 2] "foo">',
#            '<id[1 %= 2] "foo">',
#            '<id[1 ^ 2] "foo">',
#            '<id 2 < 3 "foo">',
#            '<id 2 > 3 "foo">',
#        ]
#        for string in strings:
#            try:
#                self.assertRaises(ParserError, self.parser.parse, string)
#            except AssertionError:
#                raise AssertionError("Failed to raise parser error on: " +
#                                     string)
#
#    def test_unary_expression(self):
#        #from pudb import set_trace; set_trace()
#        string = "<id[! + - 1] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '!')
#        self.assertEqual(exp['argument']['operator']['token'], '+')
#        self.assertEqual(exp['argument']['argument']['operator']['token'], '-')
#
#    def test_unary_expression_errors(self):
#        strings = [
#            '<id[a ! v] "foo">',
#            '<id[!] "foo">',
#        ]
#        for string in strings:
#            try:
#                self.assertRaises(ParserError, self.parser.parse, string)
#            except AssertionError:
#                raise AssertionError("Failed to raise parser error on: " +
#                                     string)
#
    def test_call_expression(self):
        string = "<id[foo()] 'foo'>"
        resource = self.parser.parse(string)
        exp = resource.body[0].index[0]
        self.assertEqual(exp.type, 'CallExpression')
        self.assertEqual(exp.callee.name, 'foo')
        self.assertEqual(len(exp.args), 0)

        string = "<id[foo(d, e, f, g)] 'foo'>"
        resource = self.parser.parse(string)
        exp = resource.body[0].index[0]
        self.assertEqual(exp.type, 'CallExpression')
        self.assertEqual(len(exp.args), 4)
        self.assertEqual(exp.args[0].name, 'd')
        self.assertEqual(exp.args[1].name, 'e')
        self.assertEqual(exp.args[2].name, 'f')
        self.assertEqual(exp.args[3].name, 'g')

    def test_call_expression_errors(self):
        strings = [
            '<id[1+()] "foo">',
            '<id[foo(fo fo)] "foo">',
            '<id[foo(()] "foo">',
            '<id[foo(())] "foo">',
            '<id[foo())] "foo">',
            '<id[foo("ff)] "foo">',
            '<id[foo(ff")] "foo">',
            '<id[foo(a, b, )] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_member_expression(self):
#        string = "<id[x['d']] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['name'], 'x')
#        self.assertEqual(exp['property'], 'd')
#
#        string = "<id[x.d] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['name'], 'x')
#        self.assertEqual(exp['property']['name'], 'd')
#
#        string = "<id[a||b.c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '||')
#        self.assertEqual(exp['right']['expression']['name'], 'b')
#
#        string = "<id[ x.d ] 'foo' >"
#        resource.body = self.parser.parse(string)
#
#        string = "<id[ x[ 'd' ] ] 'foo' >"
#        resource.body = self.parser.parse(string)
#
#        string = "<id[ x['d'] ] 'foo' >"
#        resource.body = self.parser.parse(string)
#
#        string = "<id[x['d']['e']] 'foo' >"
#        resource.body = self.parser.parse(string)
#
#        string = "<id[! (a?b:c)['d']['e']] 'foo' >"
#        resource.body = self.parser.parse(string)
#
    def test_member_expression_errors(self):
        strings = [
            '<id[x[[]] "foo">',
            '<id[x[] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_attr_expression(self):
#        string = "<id[x::['d']] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['name'], 'x')
#        self.assertEqual(exp['attribute'], 'd')
#
#        string = "<id[x::d] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['name'], 'x')
#        self.assertEqual(exp['attribute']['name'], 'd')
#
    def test_attr_expression_errors(self):
        strings = [
            '<id[x:::d] "foo">',
            '<id[x[::"d"]] "foo">',
            '<id[x[::::d]] "foo">',
            '<id[x:::[d]] "foo">',
            '<id[x.y::z] "foo">',
            '<id[x::y::z] "foo">',
            '<id[x.y::["z"]] "foo">',
            '<id[x::y::["z"]] "foo">',
            '<id[x::[1 "foo">',
            '<id[x()::attr1] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_parenthesis_expression(self):
#        #from pudb import set_trace; set_trace()
#        string = "<id[(1 + 2) * 3] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '*')
#        self.assertEqual(exp['left']['expression']['operator']['token'], '+')
#
#        string = "<id[(1) + ((2))] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '+')
#        self.assertEqual(exp['left']['expression'].value.source, 1)
#        self.assertEqual(exp['right']['expression']['expression'].value.source, 2)
#
#        string = "<id[(a||b).c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['expression']['operator']['token'],
#                         '||')
#        self.assertEqual(exp['property']['name'], 'c')
#
#        string = "<id[!(a||b).c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['operator']['token'], '!')
#        self.assertEqual((exp['argument']['expression']['expression']
#                          ['operator']['token']), '||')
#        self.assertEqual(exp['argument']['property']['name'], 'c')
#
#        string = "<id[a().c] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp['expression']['callee']['name'], 'a')
#        self.assertEqual(exp['property']['name'], 'c')
#
    def test_parenthesis_expression_errors(self):
        strings = [
            '<id[1+()] "foo">',
            '<id[(+)*(-)] "foo">',
            '<id[(!)] "foo">',
            '<id[(())] "foo">',
            '<id[(] "foo">',
            '<id[)] "foo">',
            '<id[1+(2] "foo">',
            '<id[a().c.[d]()] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_literal_expression(self):
#        string = "<id[012] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp.value.source, 12)
#
#    def test_literal_expression_errors(self):
#        strings = [
#            '<id[012x1] "foo">',
#        ]
#        for string in strings:
#            try:
#                self.assertRaises(ParserError, self.parser.parse, string)
#            except AssertionError:
#                raise AssertionError("Failed to raise parser error on: " +
#                                     string)
#
#    def test_value_expression(self):
#        string = "<id['foo'] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp, 'foo')
#
#        string = "<id[{a: 'foo', b: 'foo2'}] 'foo'>"
#        resource.body = self.parser.parse(string)
#        exp = resource.body[0]['index'][0]
#        self.assertEqual(exp[0].value.source, 'foo')
#        self.assertEqual(exp[1].value.source, 'foo2')
#
    def test_value_expression_errors(self):
        strings = [
            '<id[[0, 1]] "foo">',
            '<id["foo] "foo">',
            '<id[foo"] "foo">',
            '<id[["foo]] "foo">',
            '<id[{"a": "foo"}] "foo">',
            '<id[{a: 0}] "foo">',
            '<id[{a: "foo"] "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_comment(self):
#        string = "/* test */"
#        resource.body = self.parser.parse(string)
#        comment = resource.body[0]
#        self.assertEqual(comment, ' test ')
#
    def test_comment_in_entity_errors(self):
        resource = self.parser.parse('<id /* test */ "foo">')
        self.assertEqual(len(resource._errors), 2)

    def test_comment_errors(self):
        strings = [
            '/* foo ',
            'foo */',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_identifier(self):
#        #string = "<id>"
#        #resource.body = self.parser.parse(string)
#        #self.assertEqual(len(resource.body), 1)
#        #self.assertEqual(resource.body[0].id.name['name'], "id")
#
#        #string = "<ID>"
#        #resource.body = self.parser.parse(string)
#        #self.assertEqual(len(resource.body), 1)
#        #self.assertEqual(resource.body[0].id.name['name'], "ID")
#        pass
#
    def test_identifier_errors(self):
        strings = [
            '<i`d "foo">',
            '<0d "foo">',
            '<09 "foo">',
            '<i!d "foo">',
        ]
        for string in strings:
            resource = self.parser.parse(string)
            self.assertEqual(len(resource._errors), 1)

#    def test_import(self):
#        string = "import('./foo.resource.body')"
#        resource.body = self.parser.parse(string)
#        self.assertEqual(resource.body[0]['type'], 'ImportStatement')
#        self.assertEqual(resource.body[0]['uri'], './foo.resource.body')

if __name__ == '__main__':
    unittest.main()
