#!/usr/bin/env python
""" Usage: call with <filename>
"""
import os
import platform
import sys
import clang.cindex

from mako.template import Template

# pass the location of libclang to the libclang bindings library.
libclangPathWindows = "/Program Files/LLVM/bin/libclang.dll"
libclangPathMacOs = '/usr/local/Cellar/llvm/9.0.0_1/lib/libclang.dylib'

# Platform Specific config. Set libClang path and add additional compiler flags.
extraCompilerOptions = []
if platform.system() == "Windows":
    if os.path.exists(libclangPathWindows):
        clang.cindex.Config.set_library_file(libclangPathWindows)
elif platform.system() == "Darwin":
    extraCompilerOptions = ["-I/usr/local/Cellar/llvm/9.0.0_1/include/c++/v1"]
    if os.path.exists(libclangPathMacOs):
        clang.cindex.Config.set_library_file(
            libclangPathMacOs)

headerFiles = ['native/src/server.h']

index = clang.cindex.Index.create()


def get_args_for_rpc(method):
    return [{'name': arg.spelling, 'type': arg.type.spelling} for arg in method.get_arguments() if arg.kind ==
            clang.cindex.CursorKind.PARM_DECL]


def get_class_for_rpc(class_):
    methods = [{'name': method.spelling, 'returnType': method.result_type.spelling, 'args': get_args_for_rpc(method)}
               for method in class_.get_children() if method.kind == clang.cindex.CursorKind.CXX_METHOD]
    return {'name': class_.spelling, 'methods': methods}


def parse_namespace_for_rpc(ns):
    return {'name': ns.spelling, 'classes': [get_class_for_rpc(class_) for class_ in ns.get_children() if class_.kind == clang.cindex.CursorKind.CLASS_DECL and any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == 'generateRpc'])]}


def is_valid_namespace_for_rpc(ns):
    if ns.kind != clang.cindex.CursorKind.NAMESPACE:
        return False
    if any([True for class_ in ns.get_children() if class_.kind == clang.cindex.CursorKind.CLASS_DECL and any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR])]):
        return True
    return False


def process_file_for_rpc(path):
    # we need to get the path, then iterate through namespaces, classes, and headers.
    print('!!! Top of process_file_for_rpc')
    translation_unit = index.parse(
        path, ['-x', 'c++', '-std=c++17', '-D__CODE_GENERATOR__']+extraCompilerOptions)
    for diag in translation_unit.diagnostics:
        print(diag)
    namespaces = [parse_namespace_for_rpc(ns) for ns in translation_unit.cursor.get_children() if is_valid_namespace_for_rpc(ns)]
    print(namespaces)
    print('\n\n\n\n')
    original_header_name = os.path.basename(path)

    return {
        'include': original_header_name,
        'namespaces': namespaces
    }


rpc_source_template = Template(filename='rpc_source.mako')
rpc_header_template = Template(filename='rpc_header.mako')
for header in headerFiles:
    template_parameters = process_file_for_rpc(header)

    generated_header_contents = rpc_header_template.render(params=template_parameters)
    print(generated_header_contents)
    generated_source_contents = rpc_source_template.render(params=template_parameters)
    print(generated_source_contents)

    generated_header_path = os.path.splitext(header)[0] + '.gen.h'
    generated_source_path = os.path.splitext(header)[0] + '.gen.cpp'

    generated_header_file = open(generated_header_path, "w")
    n = generated_header_file.write(generated_header_contents)
    generated_header_file.close()

    generated_source_file = open(generated_source_path, "w")
    n = generated_source_file.write(generated_source_contents)
    generated_source_file.close()
