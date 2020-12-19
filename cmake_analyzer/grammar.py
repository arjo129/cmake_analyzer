import enum

"""
This file contains a parser and code generator for parsing and transforming
cmake files. (Yes it's hand written, :( )

Grammar is based on: https://cmake.org/cmake/help/latest/manual/cmake-language.7.html#grammar-token-escape-sequence
"""

class CombinatorState(enum.Enum):
    FINISHED = 0 #We finished parsing the item
    FINISHED_ONE_AFTER = 2 #For cases where look ahead is needed
    IN_PROGRESS = 1 #When the parser is parsing
    ERROR = -1 #When the parser fails

"""
This section defines the rules for a bracketed argument
"""

class BracketOpen:
    def __init__(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def reset(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACE":
            if "[" == next_char:
                self.state = "WAITING"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "WAITING":
            if "[" == next_char:
                self.state = "DONE"
                return CombinatorState.FINISHED, {"type": "bracket_open", "num_equals": self.num_equals}
            if "=" == next_char:
                self.num_equals += 1
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
            
    def code_gen(self, data):
        if data["num_equals"] == 0:
            return "[["
        return "["+ ("="*data["num_equals"]) + "["


class BracketClose:
    def __init__(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def reset(self):
        self.state = "EXPECT_BRACE"
        self.num_equals = 0

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACE":
            if "]" == next_char:
                self.state = "WAITING"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "WAITING":
            if "]" == next_char:
                return CombinatorState.FINISHED, {"type": "bracket_close", "num_equals": self.num_equals}
            if "=" == next_char:
                self.num_equals += 1
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
            
    def code_gen(self, data):
        if data["num_equals"] == 0:
            return "]]"
        return "]"+ ("="*data["num_equals"]) + "]"


class BracketArgument:
    
    def __init__(self):
        self.state = "EXPECT_BRACKET_OPEN"
        self.num_equals = 0
        self.bracket_open = BracketOpen()
        self.bracket_close = BracketClose()
        self.children = []
        self.body = ""
    
    def reset(self):
        self.state = "EXPECT_BRACKET_OPEN"
        self.num_equals = 0
        self.bracket_open = BracketOpen()
        self.bracket_close = BracketClose()
        self.children = []
        self.body = ""

    def next_char(self, next_char):
        if self.state == "EXPECT_BRACKET_OPEN":
            res, data = self.bracket_open.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_BODY"
                self.num_equals = data["num_equals"]
                self.children.append(data)
                return CombinatorState.IN_PROGRESS, None
            elif res == CombinatorState.ERROR:
                self.bracket_open.reset()
                return CombinatorState.ERROR, None
            else:
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "EXPECT_BODY":
            self.body += next_char
            res, data = self.bracket_close.next_char(next_char)
            if res == CombinatorState.FINISHED:
                if self.num_equals == data["num_equals"]:
                    self.children.append(data)
                    return CombinatorState.FINISHED, {"type": "bracket_args", "num_equals": self.num_equals, "body": self.body[:-2-self.num_equals]}
                else: 
                    self.bracket_close.reset()
                    res, data = self.bracket_close.next_char(next_char)
                    if res == CombinatorState.ERROR:
                        self.bracket_close.reset()
                    return CombinatorState.IN_PROGRESS, None

            elif res == CombinatorState.ERROR:
                self.bracket_close.reset()
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        prefix = self.bracket_open.code_gen({"type": "bracket_open", "num_equals": data["num_equals"]})
        suffix = self.bracket_close.code_gen({"type": "bracket_close", "num_equals": data["num_equals"]})
        return prefix + data["body"] + suffix


"""
This defines the rules for a quoted argument
"""
class QuotedArgument:
    def __init__(self):
        self.state = "EXPECT_QUOTE"
        self.body = ""

    def reset(self):
        self.state = "EXPECT_QUOTE"
        self.body = ""

    def next_char(self, next_char):

        if self.state == "EXPECT_QUOTE":
            if next_char == "\"":
                self.state = "EXPECT_BODY"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        
        elif self.state == "EXPECT_BODY":
            if next_char == "\\":
                self.body += next_char
                self.state = "EXPECT_ESCAPE"
                return CombinatorState.IN_PROGRESS, None
            elif next_char == "\"":
                return CombinatorState.FINISHED, {"type": "quoted_argument", "body": self.body}
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "EXPECT_ESCAPE":
            self.body += next_char
            self.state = "EXPECT_BODY"
            return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "\"" + data["body"] + "\""



"""
Handles unquoted_argument including both legacy and modern versions
Note: Finished in this case takes place after a character is read.
"""
class UnQuotedArgument:
    
    def __init__(self):
        self.state = "EXPECT_ITEM"
        self.body = ""
        self.quoted_argument = QuotedArgument()

    def reset(self):
        self.state = "EXPECT_ITEM"
        self.body = ""
        self.quoted_argument = QuotedArgument()

    def next_char(self, next_char):
        
        if self.state == "EXPECT_ITEM":
            if next_char in " ()#\t\r\n;":
                if len(self.body) == 0:
                    return CombinatorState.ERROR, None
                else:
                    return CombinatorState.FINISHED, {"type": "unquoted_argument", "body": self.body}
            elif next_char == "\\":
                self.state = "EXPECT_ESCAPE"
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None
            elif next_char == "\"":
                #stupid legacy behaviour
                self.state = "EXPECT_QUOTE" # can reuse QuotedArgument I guess
                self.quoted_argument.reset()
                self.quoted_argument.next_char(next_char)
                return CombinatorState.IN_PROGRESS, None
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_ESCAPE":
            self.state = "EXPECT_ITEM"
            self.body += next_char
            return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_QUOTE":
            res, data =self.quoted_argument.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_ITEM"
                self.body += self.quoted_argument.code_gen(data)
            return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return data["body"]



"""
Handles the line comment.
"""
class LineComment:
    def __init__(self):
        self.state = "EXPECT_HASH"
        self.body = ""

    def reset(self):
        self.state = "EXPECT_HASH"
        self.body = ""

    def next_char(self, next_char):
        if self.state == "EXPECT_HASH":
            if next_char == "#":
                self.state = "EXPECT_BODY"
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None

        elif self.state == "EXPECT_BODY":
            if next_char == "\n":
                return CombinatorState.FINISHED, {"type": "line_comment", "body": self.body}
            else:
                self.body += next_char
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "#" + data["body"] + "\n"


"""
Handles bracket comments
"""
class BracketComment:

    def __init__(self):
        self.state = "EXPECT_HASH"
        self.bracket_argument = BracketArgument()

    def reset(self):
        self.state = "EXPECT_HASH"
        self.bracket_argument = BracketArgument()

    def next_char(self, next_char):
        if self.state == "EXPECT_HASH":
            if next_char == "#":
                self.state = "EXPECT_BRACKET"
                self.bracket_argument.reset()
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None
        elif self.state == "EXPECT_BRACKET":
            res, data = self.bracket_argument.next_char(next_char)
            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, None
            elif res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "bracket_comment", "body": data}
            else:
                return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        return "#"+self.bracket_argument.code_gen(data["body"])

"""
Handles Comments
"""
class Comment:

    def __init__(self):
        self.state = "EXPECT_HASH"
        self.bracket_comment = BracketComment()
        self.line_comment = LineComment()

    def reset(self):
        self.state = "EXPECT_HASH"
        self.bracket_comment = BracketComment()
        self.line_comment = LineComment()

    
    def next_char(self, next_char):

        if self.state == "EXPECT_HASH":
            self.bracket_comment.reset()
            self.line_comment.reset()
            self.bracket_comment.next_char(next_char)
            res, _ = self.line_comment.next_char(next_char)
            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, None
            if res == CombinatorState.IN_PROGRESS:
                self.state = "DETERMINE_TYPE"
                return CombinatorState.IN_PROGRESS, None

        elif self.state == "DETERMINE_TYPE":
            res_bc, _  = self.bracket_comment.next_char(next_char)
            res_lc, _ = self.line_comment.next_char(next_char)
            if res_bc == CombinatorState.ERROR:
                if res_lc == CombinatorState.ERROR:
                    return CombinatorState.ERROR, None
                else:
                    self.state = "LINE_COMMENT"
                    return CombinatorState.IN_PROGRESS, None
            else:
                self.state = "BRACKET_COMMENT"
                return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "LINE_COMMENT":
            res, data = self.line_comment.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "comment", "comment": "line", "body": data}
            return res, None

        elif self.state == "BRACKET_COMMENT":
            self.line_comment.next_char(next_char)
            res, data = self.bracket_comment.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED, {"type": "comment", "comment": "bracket", "body": data}

            if res == CombinatorState.ERROR: 
                #Not in grammar spec just here to allow for malformed comments in older files
                #Handles malformatted comments like "#[ Some comment".
                self.state = "LINE_COMMENT"
                return CombinatorState.IN_PROGRESS, None
            return res, None

    def code_gen(self, data):

        if data["comment"] == "line":
            return self.line_comment.code_gen(data["body"])

        elif data["comment"] == "bracket":
            return self.bracket_comment.code_gen(data["body"])


"""
Handles delimiters
"""
class ArgumentSeperator:
    def __init__(self):
        self.body = ""

    def reset(self):
        self.body = ""

    def next_char(self, next_char):
        
        if next_char in " \t\n\r;":
            self.body += next_char
            return CombinatorState.IN_PROGRESS, None
        
        elif len(self.body) == 0:
            return CombinatorState.ERROR, None
        
        else:
            return CombinatorState.FINISHED_ONE_AFTER, {"type": "whitespace", "body": self.body}

    def code_gen(self, data):
        return data["body"]


"""
Handle arguments
"""
class Argument:
    def __init__(self):
        self.state = "EXPECT_ARGUMENT"
        self.bracketed_argument = BracketArgument()
        self.quoted_argument = QuotedArgument()
        self.unquoted_argument = UnQuotedArgument()

    def reset(self):
        self.state = "EXPECT_ARGUMENT"
        self.bracketed_argument.reset()
        self.quoted_argument.reset()
        self.unquoted_argument.reset()
    
    def next_char(self, next_char):
        if self.state == "EXPECT_ARGUMENT":
            res_brac, _ = self.bracketed_argument.next_char(next_char)
            res_quote, _ = self.quoted_argument.next_char(next_char)
            res_unquoted, arg = self.unquoted_argument.next_char(next_char)

            if res_brac == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_BRAC_ARG"
                return CombinatorState.IN_PROGRESS, None
            
            if res_quote == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_QUOTE"
                return CombinatorState.IN_PROGRESS, None

            if res_unquoted == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_UNQUOTED"
                return CombinatorState.IN_PROGRESS, None
            
            return CombinatorState.ERROR, None

        elif self.state == "EXPECT_BRAC_ARG":
            res, data = self.bracketed_argument.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return res, {"type": "argument", "body": data, "argument_type": "bracket"}
            return res , None
        
        elif self.state == "EXPECT_QUOTE":
            res, data = self.quoted_argument.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return res, {"type": "argument", "body": data, "argument_type": "quote"}
            return res , None

        elif self.state == "EXPECT_UNQUOTED":
            res, data = self.unquoted_argument.next_char(next_char)
            if res == CombinatorState.FINISHED:
                return CombinatorState.FINISHED_ONE_AFTER, {"type": "argument", "body": data, "argument_type": "unquoted"}
            return res, None

    def code_gen(self, data):
        if data["argument_type"] == "unquoted":
            return self.unquoted_argument.code_gen(data["body"])
        
        elif data["argument_type"] == "quote":
            return self.quoted_argument.code_gen(data["body"])
        
        elif data["argument_type"] == "bracket":
            return self.bracketed_argument.code_gen(data["body"])

"""
Handle command arguments.
"""
class CommandArguments:
    
    def __init__(self):
        self.parenthesis = []
        self.state = "EXPECT_PAREN"
        self.argument_parser = Argument()
        self.comment_parser = Comment()
        self.separator_parser = ArgumentSeperator()
        self.body = [{"type": "lparenthesis"}]

    def reset(self):
        self.parenthesis = []
        self.state = "EXPECT_PAREN"
        self.argument_parser.reset()
        self.comment_parser.reset()
        self.separator_parser.reset()
        self.body = [{"type": "lparenthesis"}]

    def next_char(self, next_char):

        if self.state == "EXPECT_PAREN":
            if next_char == "(":
                self.state = "EXPECT_BODY"
                self.parenthesis.append("(")
                return CombinatorState.IN_PROGRESS, None
            else:
                return CombinatorState.ERROR, None

        if self.state == "EXPECT_BODY":
            if next_char == "(":
                self.parenthesis.append("(")
                self.body.append({"type": "lparenthesis"})
                return CombinatorState.IN_PROGRESS, None

            if next_char == ")":
                self.parenthesis.pop()
                self.body.append({"type": "rparenthesis"})
                if len(self.parenthesis) == 0:

                    return CombinatorState.FINISHED, {"type": "argument_list", "body": self.body}
                return CombinatorState.IN_PROGRESS, None

            res, _ = self.comment_parser.next_char(next_char)
            if res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_COMMENT"
                return res, None
            
            res, _ = self.argument_parser.next_char(next_char)
            if res != CombinatorState.ERROR:
                self.state = "EXPECT_ARG"
                return res, None

            res, _ = self.separator_parser.next_char(next_char)
            if res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_SPACE"
                return res, None

            return CombinatorState.ERROR, None
        
        if self.state == "EXPECT_ARG":
            
            res, data = self.argument_parser.next_char(next_char)
            
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_BODY"
                self.body.append(data)
                self.argument_parser.reset()

            if res == CombinatorState.FINISHED_ONE_AFTER:
                self.state = "EXPECT_BODY"
                self.body.append(data)
                self.argument_parser.reset()
                return self.next_char(next_char) # look ahead

            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, data
            
            return CombinatorState.IN_PROGRESS, None
        
        if self.state == "EXPECT_SPACE":
            
            res, data = self.separator_parser.next_char(next_char)

            if res == CombinatorState.FINISHED_ONE_AFTER:
                self.state = "EXPECT_BODY"
                self.body.append(data)
                self.separator_parser.reset()
                return self.next_char(next_char) # look ahead

            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, data
            
            return CombinatorState.IN_PROGRESS, None

        if self.state == "EXPECT_COMMENT":
            
            res, data = self.comment_parser.next_char(next_char)

            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_BODY"
                self.body.append(data)
                self.comment_parser.reset()

            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, data
            
            return CombinatorState.IN_PROGRESS, None

    def code_gen(self, data):
        result = ""
        for item in data["body"]: 
            if item["type"] == "lparenthesis":
                result += "("
            elif item["type"] == "rparenthesis":
                result += ")"
            elif item["type"] == "argument":
                result += self.argument_parser.code_gen(item)
            elif item["type"] == "whitespace":
                result += self.separator_parser.code_gen(item)
            elif item["type"] == "comment":
                result += self.comment_parser.code_gen(item)
        return result

"""
Handles commands in their full glory
"""
class Command:
    def __init__(self):
        self.state = "EXPECT_START"
        self.command_parser = UnQuotedArgument() #TODO CREATE A LITERAL PARSER....
        self.space_parser = ArgumentSeperator()
        self.argument_parser = CommandArguments()
        self.command = {}
        self.separators = {}
        self.command_argument = {}

    def reset(self):
        self.command_parser.reset()
        self.space_parser.reset()
        self.argument_parser.reset()
        self.command = {}
        self.separators = {}
        self.command_argument = {}

    def next_char(self, next_char):

        if self.state == "EXPECT_START":
            res, _ = self.command_parser.next_char(next_char)
            if res == CombinatorState.ERROR:
                return CombinatorState.ERROR, _
            elif res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_LITERAL"
                return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_LITERAL":
            res, data = self.command_parser.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_SPACE"
                self.command = data["body"]
                return self.next_char(next_char)

            elif res == CombinatorState.ERROR:
                return CombinatorState.ERROR, data
            
            return CombinatorState.IN_PROGRESS, None
        
        elif self.state == "EXPECT_SPACE":
            res, data = self.space_parser.next_char(next_char)
            if res == CombinatorState.FINISHED_ONE_AFTER or res == CombinatorState.ERROR:
                self.state = "EXPECT_ARGUMENTS"
                if data:
                    self.separators = data
                return self.next_char(next_char)

            return CombinatorState.IN_PROGRESS, None

        elif self.state == "EXPECT_ARGUMENTS":
            res, data = self.argument_parser.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.command_argument = data
                return CombinatorState.FINISHED, {"type": "command", "command": self.command, "separator": self.separators, "parameters": self.command_argument}
            return res, None
    
    def code_gen(self, data):
        if data["separator"] == {}:
            return data["command"] + self.argument_parser.code_gen(data["parameters"])
        else:
            return data["command"] + self.space_parser.code_gen(data["separator"]) + self.argument_parser.code_gen(data["parameters"])


"""
Top level CMakeList handler
"""
class CMakeFile:
    def __init__(self):
        self.comment_parser = Comment()
        self.command_parser = Command()
        self.space_parser = ArgumentSeperator()
        self.body = []
        self.state = "EXPECT_ANYTHING"

    def get_ast(self):
        if self.state != "EXPECT_ANYTHING":
            raise Exception("File is not complete") # TODO: Improve errors
        return self.body
    
    def next_char(self, next_char):
        if self.state == "EXPECT_ANYTHING":
            self.comment_parser.reset()
            self.command_parser.reset()
            self.space_parser.reset()
            
            res, _  = self.comment_parser.next_char(next_char)
            if res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_COMMENT"
                return CombinatorState.IN_PROGRESS, None
            
            res, _ = self.space_parser.next_char(next_char)
            if res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_SPACE"
                return CombinatorState.IN_PROGRESS, None
            
            res, _ = self.command_parser.next_char(next_char)
            if res == CombinatorState.IN_PROGRESS:
                self.state = "EXPECT_COMMAND"
                return CombinatorState.IN_PROGRESS, None

            #Should be unreachable
        
        elif self.state == "EXPECT_COMMENT":
            res, data  = self.comment_parser.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_ANYTHING"
                self.body.append(data)
                return CombinatorState.IN_PROGRESS, None
            return res, None

        elif self.state == "EXPECT_COMMAND":
            res, data  = self.command_parser.next_char(next_char)
            if res == CombinatorState.FINISHED:
                self.state = "EXPECT_ANYTHING"
                self.body.append(data)
                return CombinatorState.IN_PROGRESS, None
            return res, None
        
        elif self.state == "EXPECT_SPACE":
            res, data  = self.space_parser.next_char(next_char)
            if res == CombinatorState.FINISHED_ONE_AFTER:
                self.state = "EXPECT_ANYTHING"
                self.body.append(data)
                return self.next_char(next_char)
            return res, None


def get_ast(input_string):
    """
    Builds an Abstract Syntax Tree (AST) given a CMake file.
    input_string - a string containing the contents of the CMakeFile
    """
    cmake_parser = CMakeFile()
    for character in input_string:
        res, data = cmake_parser.next_char(character)
        if res != CombinatorState.IN_PROGRESS:
            raise Exception(data)
    return cmake_parser.get_ast()

def ast_to_string(ast):
    """
    Converts AST back to string
    """
    if not isinstance(ast, list):
        raise Exception("AST must be a list!!")

    result = ""

    for item in ast:
        if "type" not in item:
            raise Exception("Could not get type of element "+str(item))

        if item["type"] == "command":
            result += Command().code_gen(item)
        elif item["type"] == "comment":
            result += Comment().code_gen(item)
        elif item["type"] == "whitespace":
            result += ArgumentSeperator().code_gen(item)
    return result