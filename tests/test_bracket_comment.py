from cmake_analyzer.grammar import BracketComment, CombinatorState
import unittest


def parse_item(inp):
    bc = BracketComment()
    for x in inp:
        res, data = bc.next_char(x)
    return res,data

class TestBracketComment(unittest.TestCase):
    
    def test_bracket_comment_no_equals(self):
        #normal operation
        res, data = parse_item("#[[Hello world]]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'type': 'bracket_comment', 'body': {'body': 'Hello world', 'type': 'bracket_args', 'num_equals': 0}})

    def test_bracket_comment_not_bracket(self):
        res, data = parse_item("some rubbish")
        self.assertEqual(res, CombinatorState.ERROR)

    def test_bracket_comment_idempotency(self):
        in_str = "#[==[Hello world]=]=]==]"
        res, data = parse_item(in_str)
        bc = BracketComment()
        res = bc.code_gen(data)
        self.assertEqual(in_str, res)