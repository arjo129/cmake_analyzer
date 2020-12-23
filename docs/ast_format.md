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


## Comments

CMake files have two comment formats: The line comment and a bracket 
comment. A line comment looks something like:

```
# Some comment
```

It starts witha a "#" and ends with a new line (or EOF). When the above is 
passed to the `get_ast` function it will return a dict like:

```
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
```
#[=[Hello
 world]=]
```
Note that there must be an equal number of equals sign. The corresponding 
output is something like this:
```
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

