#!/usr/bin/env python
import os
import platform
import sys
import clang.cindex

from mako.template import Template
from name_convert import convert_name, convert_type

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

headerFiles = ['native/src/server.h', 'native/src/render_data.h']

index = clang.cindex.Index.create()


def is_class_or_struct(cursor):
    return cursor.kind == clang.cindex.CursorKind.CLASS_DECL or cursor.kind == clang.cindex.CursorKind.STRUCT_DECL


def get_args_for_rpc(method):
    return [{'name': arg.spelling, 'type': arg.type.spelling} for arg in method.get_arguments() if arg.kind ==
            clang.cindex.CursorKind.PARM_DECL]


def get_class_for_rpc(class_):
    methods = [{'name': method.spelling, 'returnType': method.result_type.spelling, 'args': get_args_for_rpc(method)}
               for method in class_.get_children() if method.kind == clang.cindex.CursorKind.CXX_METHOD]
    return {'name': class_.spelling, 'methods': methods}


def parse_namespace_for_rpc(ns):
    return {'name': ns.spelling, 'classes': [get_class_for_rpc(class_) for class_ in ns.get_children() if is_class_or_struct(class_) and any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == 'generateRpc'])]}


def is_valid_namespace_for_rpc(ns):
    if ns.kind != clang.cindex.CursorKind.NAMESPACE:
        return False
    if any([True for class_ in ns.get_children() if is_class_or_struct(class_) and any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR])]):
        return True
    return False


def process_file_for_rpc(path):
    # we need to get the path, then iterate through namespaces, classes, and headers.
    translation_unit = index.parse(
        path, ['-x', 'c++', '-std=c++17', '-D__CODE_GENERATOR__']+extraCompilerOptions)
    for diag in translation_unit.diagnostics:
        print(diag)
    namespaces = [parse_namespace_for_rpc(ns) for ns in translation_unit.cursor.get_children() if is_valid_namespace_for_rpc(ns)]
    original_header_name = os.path.basename(path)
    return {
        'include': original_header_name,
        'namespaces': namespaces
    }


# this recursively finds and parses the members of all classes at and below the provided cursor.
def get_class_for_cereal(class_, path=''):
    classes = []
    members = [{'name': member.spelling, 'json_name': convert_name(member.spelling), 'ts_type': convert_type(member.type.spelling)}
               for member in class_.get_children() if member.kind == clang.cindex.CursorKind.FIELD_DECL]
    classes.append({'name': concatenate_namespaces(path, class_.spelling), 'members': members, 'ts_name': class_.spelling})
    for child in class_.get_children():
        if(is_class_or_struct(child)):
            classes.extend(get_class_for_cereal(child, concatenate_namespaces(path, class_.spelling)))
    return classes


def parse_namespace_for_cereal(ns, path):
    # classes is now a nested list we need to flatten
    classes = [get_class_for_cereal(class_) for class_ in ns.get_children() if is_class_or_struct(class_) and any(
        [c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == 'generateCereal'])]

    classes = [class_ for class_list in classes for class_ in class_list]
    return {'name': path, 'classes': classes}


def is_valid_class_for_cereal(class_):
    if (not is_class_or_struct(class_)):
        return False
    if not any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == 'generateCereal']):
        return False
    return True


def is_valid_namespace_for_cereal(ns):
    if ns.kind != clang.cindex.CursorKind.NAMESPACE:
        return False
    if any([is_valid_class_for_cereal(class_) for class_ in ns.get_children()]):
        return True
    return False


# helper function to handle adding '::' between namespaces.
def concatenate_namespaces(base, new):
    if base == '':
        return new
    return base + '::' + new


# this extracts the namespace cursor and complete name (including ::) for all namespaces bellow the root.
# this recursively explores all namespaces.
def get_namespace_cursors(translation_unit_cursor, namespace_path=''):
    namespace_cursors = []
    for child in translation_unit_cursor.get_children():
        if(is_valid_namespace_for_cereal(child)):
            namespace_cursors.append({'cursor': child, 'path': concatenate_namespaces(namespace_path, child.spelling)})
        if(child.kind == clang.cindex.CursorKind.NAMESPACE and any([is_valid_namespace_for_cereal(grandchild) for grandchild in child.get_children()])):
            namespace_cursors.extend(get_namespace_cursors(child, child.spelling))
    return namespace_cursors


def process_file_for_cereal(path):
    # we need to get the path, then iterate through namespaces, classes, and headers.
    translation_unit = index.parse(
        path, ['-x', 'c++', '-std=c++17', '-D__CODE_GENERATOR__']+extraCompilerOptions)
    for diag in translation_unit.diagnostics:
        print(diag)
    namespace_cursors = get_namespace_cursors(translation_unit.cursor)
    namespaces = [parse_namespace_for_cereal(ns['cursor'], ns['path']) for ns in namespace_cursors]
    original_header_name = os.path.basename(path)

    return {
        'include': original_header_name,
        'namespaces': namespaces
    }


# loop through all provided headerFiles and generate cereal conversion functions.
cereal_header_template = Template(filename='cereal_header.mako')
cereal_ts_template = Template(filename='cereal_ts.mako')
for header in headerFiles:
    template_parameters = process_file_for_cereal(header)
    if(len(template_parameters['namespaces']) == 0):
        print('no GENERATE_CEREAL classes found in ' + header)
        continue

    generated_header_contents = cereal_header_template.render(params=template_parameters)
    print(generated_header_contents)
    generated_ts_contents = cereal_ts_template.render(params=template_parameters)
    print(generated_ts_contents)

    generated_header_path = os.path.splitext(header)[0] + '.gen.h'

    generated_header_file = open(generated_header_path, "w")
    n = generated_header_file.write(generated_header_contents)
    generated_header_file.close()

    generated_ts_path = os.path.splitext(header)[0] + '.gen.ts'

    generated_ts_file = open(generated_ts_path, "w")
    n = generated_ts_file.write(generated_ts_contents)
    generated_ts_file.close()

# loop through all headerFiles and generate RPC files
rpc_source_template = Template(filename='rpc_source.mako')
rpc_header_template = Template(filename='rpc_header.mako')
for header in headerFiles:
    template_parameters = process_file_for_rpc(header)
    if(len(template_parameters['namespaces']) == 0):
        print('no GENERATE_RPC classes found in ' + header)
        continue

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
