# AST Format reference

The `get_ast` function returns a list of dicts. Each dict represents a 
certain structure.

## Generic structure of an AST

An AST is essentially a dictionary. Each node of the dictionary contains a 
`"type"` field which dictates the type of the node. There are several values which `"type"` may take on:
* `comment` - Generic comment type
* `line_comment` - A line comment
* `bracket_comment` - A Bracket Comment
* `bracket_args` - A Bracket Argument
* `command` - A command
* `whitespace` - A set of white spaces
* `lparenthesis` - A left parenthesis
* `rparenthesis` - A right parenthesis
* `argument_list` - An argument list

## Comments

CMake files have two comment formats: The line comment and a bracket 
comment. A line comment looks something like:

```CMake
# Some comment
```

It starts witha a "#" and ends with a new line (or EOF). When the above is 
passed to the `get_ast` function it will return a dict like:

```python
{
    "type": "comment", 
    "comment": "line", 
    "body":{
        "type": "line_comment", 
        "body": " Some Comment"
    }
}
```

Bracket comments on the other hand look something like this:
```CMake
#[=[Hello
 world]=]
```
Note that there must be an equal number of equals sign. The corresponding 
output is something like this:
```python
{
    "type": "comment", 
    "comment": "bracket", 
    "body":{
        "type": "bracket_comment",
        "body": 
        {
            "type": "bracket_args", 
            "num_equals": 1, 
            "body": "Hello\n world"
        }
    }
}
```

## Commands

Commands make up a large part of the `cmake` macro language. An example command
looks something like:

```CMake
find_package ( CATKIN_PACKAGES
roscpp
    #octomap_msgs
    )
```
This results in the following parse tree.
```python
{
    'command': 'find_package', 
    'type': 'command', 
    'separator': {'body': ' ', 'type': 'whitespace'}, 
    'parameters': {
        'body': [
            {'type': 'lparenthesis'}, 
            {'body': ' ', 'type': 'whitespace'}, 
            {'body': {'body': 'CATKIN_PACKAGES', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
            {'body': '\n', 'type': 'whitespace'}, 
            {'body': {'body': 'roscpp', 'type': 'unquoted_argument'}, 'type': 'argument', 'argument_type': 'unquoted'}, 
            {'body': '\n\t', 'type': 'whitespace'}, 
            {'comment': 'line', 'body': {'body': 'octomap_msgs', 'type': 'line_comment'}, 'type': 'comment'}, 
            {'body': '\t', 'type': 'whitespace'}, 
            {'type': 'rparenthesis'}
            ],
        'type': 'argument_list'
        }
}
```
Notice the AST contains both whitespace and 