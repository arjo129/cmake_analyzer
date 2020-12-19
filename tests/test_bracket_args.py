from cmake_analyzer.grammar import BracketArgument, CombinatorState
import unittest


def parse_item(inp):
    ba = BracketArgument()
    for x in inp:
        res, data = ba.next_char(x)
    return res,data

class TestBracketArguments(unittest.TestCase):
    
    def test_bracket_argument_no_equals(self):
        #normal operation
        res, data = parse_item("[[Hello world]]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world', 'type': 'bracket_args', 'num_equals': 0})
    
    def test_bracket_argument_imbalanced_equals(self):
        res, data = parse_item("[[Hello world]=]")
        self.assertEqual(res, CombinatorState.IN_PROGRESS)

    def test_bracket_argument_few_equals(self):    
        res, data = parse_item("[=[Hello world]=]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world', 'type': 'bracket_args', 'num_equals': 1})

    def test_bracket_argument_corner_cases(self):
        res, data = parse_item("[==[Hello world]=]==]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world]=', 'type': 'bracket_args', 'num_equals': 2})
        
        res, data = parse_item("[==[Hello world]=]=]==]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world]=]=', 'type': 'bracket_args', 'num_equals': 2})

    def test_bracket_argument_not_bracket(self):
        res, data = parse_item("some rubbish")
        self.assertEqual(res, CombinatorState.ERROR)

    def test_bracket_argument_idempotency(self):
        in_str = "[==[Hello world]=]=]==]"
        res, data = parse_item(in_str)
        ba = BracketArgument()
        res = ba.code_gen(data)
        self.assertEqual(in_str, res)