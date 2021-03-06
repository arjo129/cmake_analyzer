from cmake_analyzer.grammar import LineComment, CombinatorState
import unittest

def parse_item(inp):
    lc = LineComment()
    for x in inp:
        res, data = lc.next_char(x)
    return res,data

class TestLineComment(unittest.TestCase):
    
    def test_line_comment(self):
        #normal operation
        res, data = parse_item("#Hello world\n")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {'body': 'Hello world', 'type': 'line_comment', 'terminates': '\n'})

    def test_line_comment_not_comment(self):
        #normal operation
        res, data = parse_item("Hello\n")
        self.assertEqual(res, CombinatorState.ERROR)
    
    def test_line_comment_idempotent(self):
        inp = "#Hello world\n"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = LineComment().code_gen(data)
        self.assertEqual(inp, out)
