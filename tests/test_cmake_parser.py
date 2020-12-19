from cmake_analyzer.grammar import get_ast, ast_to_string
import unittest

class TestWholeFile(unittest.TestCase):
    
    def test_simple_file(self):
        #normal operation
        inp = "find_package ( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t) #Test File Parsing\n"
        ast = get_ast(inp)
        self.assertEqual(ast,[{'type': 'command', 'command': 'find_package', 'separator': {'type': 'whitespace', 'body': ' '}, 'parameters': {'type': 'argument_list', 'body': [{'type': 'lparenthesis'}, {'type': 'whitespace', 'body': ' '}, {'type': 'argument', 'body': {'type': 'unquoted_argument', 'body': 'CATKIN_PACKAGES'}, 'argument_type': 'unquoted'}, {'type': 'whitespace', 'body': '\n'}, {'type': 'argument', 'body': {'type': 'unquoted_argument', 'body': 'roscpp'}, 'argument_type': 'unquoted'}, {'type': 'whitespace', 'body': '\n\t'}, {'type': 'comment', 'comment': 'line', 'body': {'type': 'line_comment', 'body': 'octomap_msgs'}}, {'type': 'whitespace', 'body': '\t'}, {'type': 'rparenthesis'}]}}, {'type': 'whitespace', 'body': ' '}, {'type': 'comment', 'comment': 'line', 'body': {'type': 'line_comment', 'body': 'Test File Parsing'}}])

    def test_simple_idempotency(self):
        inp = "find_package ( CATKIN_PACKAGES\nroscpp\n\t#octomap_msgs\n\t) #Test File Parsing\n"
        out = ast_to_string(get_ast(inp))
        self.assertEqual(inp, out)
