from cmake_analyzer.grammar import QuotedArgument, CombinatorState
import unittest

def parse_item(inp):
    qa = QuotedArgument()
    for x in inp:
        res, data = qa.next_char(x)
    return res,data

class TestQuotedArguments(unittest.TestCase):
    
    def test_bracket_argument_ok(self):
        #normal operation
        res, data = parse_item("\"Hello world\"")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world', 'type': 'quoted_argument'})

    def test_bracket_argument_with_escape(self):
        res, data = parse_item("\"Hello world\\\"\"")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world\\\"', 'type': 'quoted_argument'})

    def test_bracket_argument_with_not_arg(self):
        res, data = parse_item("Hello world")
        self.assertEqual(res, CombinatorState.ERROR)

    def test_bracket_argument_idempotency(self):
        inp = "\"Hello world\\\"\""
        res, data = parse_item(inp)
        qa = QuotedArgument()
        out = qa.code_gen(data)
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertEqual(out, inp)