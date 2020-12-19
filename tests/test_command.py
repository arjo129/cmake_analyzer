from cmake_analyzer.grammar import Command, CombinatorState
import unittest


def parse_item(inp):
    bc = Command()
    for x in inp:
        res, data = bc.next_char(x)
    return res,data

class TestCommandArguments(unittest.TestCase):
    
    def test_command_argument_1(self):
        #normal operation
        inp = "find_package ( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, 
            {'command': 'find_package', 
            'type': 'command', 
            'separator': {'body': ' ', 'type': 'whitespace'}, 
            'parameters': {'body': [{'type': 'lparenthesis'}, 
                        {'body': ' ', 'type': 'whitespace'}, 
                        {'body': {'body': 'CATKIN_PACKAGES', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
                        {'body': '\n', 'type': 'whitespace'}, 
                        {'body': {'body': 'roscpp', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
                        {'body': '\n\t', 'type': 'whitespace'}, 
                        {'comment': 'line', 'body': {'body': 'octomap_msgs', 'type': 'line_comment'}, 'type': 'comment'}, 
                        {'body': '\t', 'type': 'whitespace'}, 
                        {'type': 'rparenthesis'}], 'type': 'argument_list'}})

    def test_command_argument_2(self):
        #normal operation
        inp = "find_package( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        self.assertDictEqual(data, 
            {'command': 'find_package', 
            'type': 'command', 
            'separator': {}, 
            'parameters': {'body': [{'type': 'lparenthesis'}, 
                        {'body': ' ', 'type': 'whitespace'}, 
                        {'body': {'body': 'CATKIN_PACKAGES', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
                        {'body': '\n', 'type': 'whitespace'}, 
                        {'body': {'body': 'roscpp', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
                        {'body': '\n\t', 'type': 'whitespace'}, 
                        {'comment': 'line', 'body': {'body': 'octomap_msgs', 'type': 'line_comment'}, 'type': 'comment'}, 
                        {'body': '\t', 'type': 'whitespace'}, 
                        {'type': 'rparenthesis'}], 'type': 'argument_list'}})

    def test_command_idempotency_1(self):
        #normal operation
        inp = "find_package ( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = Command().code_gen(data)
        self.assertEqual(inp, out)

    def test_command_idempotency_2(self):
        #normal operation
        inp = "find_package( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t)"
        res, data = parse_item(inp)
        self.assertEqual(res, CombinatorState.FINISHED)
        out = Command().code_gen(data)
        self.assertEqual(inp, out)