# CMake Analyzer

The `cmake_analyzer` module contains two functions which can be used to 
create an AST (Abstract Syntax Tree) given a `cmakelist.txt`. Your code 
can then manipulate the AST 
to output a new cmake file. This makes advanced code analysis possible for 
your tools. It also provides a building block for our intelligent cmake 
editing features possible. 

## Usage

To parse an AST one may simply call 
```
from cmake_analyzer.grammar import get_ast

with open("CMakeLists.txt") as f:
    ast = get_ast(f.read())
```

## Additional Documentation
For additional documentation see the `examples` folder or the 
[ast format](docs/ast_format.md) reference. 

