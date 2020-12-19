from cmake_analyzer.grammar import Comment, CombinatorState
import unittest


def parse_item(inp):
    bc = Comment()
    for x in inp:
        res, data = bc.next_char(x)
    return res,data

class TestComment(unittest.TestCase):
    
    def test_bracket_comment_no_equals(self):
        #normal operation
        res, data = parse_item("#[[Hello\n world]]")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {"type": "comment", "comment": "bracket", "body":{
            "type": "bracket_comment", "body": {
                "type": "bracket_args", "num_equals": 0, "body": "Hello\n world"
            }
        }})

    def test_line_comment_no_equals(self):
        #normal operation
        res, data = parse_item("#Hello world\n")
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, {"type": "comment", "comment": "line", "body":{
            "type": "line_comment", "body": "Hello world"
        }})

    def test_not_comment(self):
        #normal operation
        res, data = parse_item("hello world")
        self.assertEqual(res, CombinatorState.ERROR)

    def test_comment_idempotency(self):
        inp = "#Hello world\n"
        res, data = parse_item(inp)
        out = Comment().code_gen(data)
        self.assertEqual(inp, out)

        inp = "#[[Hello world\n]]"
        res, data = parse_item(inp)
        out = Comment().code_gen(data)
        self.assertEqual(inp, out)

        #technically an illegal comment
        inp = "#[=Hello world\n"
        res, data = parse_item(inp)
        out = Comment().code_gen(data)
        self.assertEqual(inp, out)

        #technically an illegal comment
        inp = "#[Hello world\n"
        res, data = parse_item(inp)
        out = Comment().code_gen(data)
        self.assertEqual(inp, out)
