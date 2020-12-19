from cmake_analyzer.grammar import UnQuotedArgument, CombinatorState
import unittest


def parse_item(inp):
    ba = UnQuotedArgument()
    for x in inp:
        res, data = ba.next_char(x)
    return res,data

class TestUnquotedArguments(unittest.TestCase):
    
    def test_unquoted_argument_default(self):
        res, data = parse_item("helloworld ")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'helloworld', 'type': 'unquoted_argument'})

    def test_unquoted_argument_with_embedded_quote(self):
        res, data = parse_item("hello\" \"world;")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'hello\" \"world', 'type': 'unquoted_argument'})
    
    def test_unquoted_argument_escaped(self):
        res, data = parse_item("hello\\ world ")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'hello\\ world', 'type': 'unquoted_argument'})

    def test_idempotency(self):
        inp = "hello\\ world "
        res, data = parse_item(inp)
        out = UnQuotedArgument().code_gen(data)
        self.assertEqual(inp[:-1], out)
