# JSON RPC C++ Prototype

This is a python code generator that generates serialization code to support serializing C++ classes and reading them in typescript.

It's a very crude prototype, which is why everything is a mess.

This is based on these articles:

- https://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang
- http://szelei.me/code-generator/

## Requirements

- clang
- libclang language bindings
- mako
- python3
- cmake
- [Sourcetrail VS extension](https://marketplace.visualstudio.com/items?itemName=vs-publisher-1208751.SourcetrailExtension) (for creating compile_commands.json on windows)

## Setup

```bash
pip3 install clang
pip3 install mako
python3 generate.py
cd native
mkdir build
cd build
cmake ..
cmake --build .
./main
```

Note: the path to the libclang library either needs to be on `$LD_LIBRARY_PATH` or passed to `clang.cindex.Config.set_library_file` in code.

Note: clang for windows can be downloaded here: http://releases.llvm.org/download.html#9.0.0

## Goals:

1. [deprecated] RPC system to call GraphServer functions from the front-end
2. typescript types for these RPC calls.
3. cereal C++ library serialize code for actions, state, and data objects.

## Downsides

1. We will have to add new "ArchiveJson" functions for every container type (unordered_map, optional, variant, etc) just like we do now.
2. We will need to constantly expand the typescript conversion code to handle new container types, new type aliases, etc.
3. Not sure our rapidjson implementation is maximally efficient?
