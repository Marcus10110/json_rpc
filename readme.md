# JSON RPC C++ Prototype

This is a python code generator that generates serialization code to support calling methods on a class using json messages.

It's a very crude prototype, which is why everything is a mess.

This is based on these articles:
https://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang
http://szelei.me/code-generator/


## Requirements:
- clang installed
- libclang language bindings installed
- python3
- cmake

## Setup:
```bash
pip3 install clang
python3 generate.py
cd native
mkdir build
cd build
cmake ..
make
./main
```

*Note: the path to the libclang library is currently hard-coded into the python file, and set to `/usr/local/Cellar/llvm/9.0.0_1/lib/libclang.dylib`. This will probably need to be edited.*

## Goals:
1. RPC system to call GraphServer functions from the front-end
2. typescript types for these RPC calls.
3. cereal C++ library serialize code for actions, state, and data objects.