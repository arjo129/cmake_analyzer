from cmake_analyzer.grammar import CommandArguments, CombinatorState
import unittest


def parse_item(inp):
    bc = CommandArguments()
    for x in inp:
        res, data = bc.next_char(x)
    return res,data

class TestCommandArguments(unittest.TestCase):
    
    def test_command_arguments_1(self):
        #normal operation
        inp = "( #[[Hello world]] [[some nonsense (]] (A AND B))"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = CommandArguments().code_gen(data)
        self.assertEqual(out, inp)

    def test_command_arguments_2(self):
        #normal operation
        inp = "( test )"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = CommandArguments().code_gen(data)
        self.assertEqual(out, inp)

    def test_command_arguments_3(self):
        #normal operation
        inp = "( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = CommandArguments().code_gen(data)
        self.assertEqual(out, inp)

    def test_command_arguments_4(self):
        #normal operation
        inp = "(CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = CommandArguments().code_gen(data)
        self.assertEqual(out, inp)