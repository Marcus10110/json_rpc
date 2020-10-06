#!/usr/bin/env python
from io import StringIO
import os
import platform
import sys
import clang.cindex
from typing import List, Dict, Tuple, Sequence, TypedDict, Any, NamedTuple, Set
from name_convert import convert_name_for_json, convert_type_for_ts
from pprint import pprint

# For a given header file, let's step through each top-level namespace.
# check if the namespace contains any classes or structs that have a "ANNOTATE_ATTR" attached (manually tagged) with the 'generateRpc' value.
# for each of these classes/structs, extract:
# namespace
# class name
# data members (type, name)
# methods (return type, name, arguments(name, type))


class NamespaceCursor(TypedDict):
    cursor: Any
    path: str


class Member(TypedDict):
    name: str
    json_name: str
    ts_type: str


class Arg(TypedDict):
    name: str
    type: str


class Method(TypedDict):
    name: str
    return_type: str
    args: List[Arg]


class ParsedClass(TypedDict):
    name: str
    full_name: str
    members: List[Member]
    methods: List[Method]
    extends_data: bool


class Namespace(TypedDict):
    name: str
    classes: List[ParsedClass]


class ParsedHeader(TypedDict):
    include: str
    namespaces: List[Namespace]


annotation_tag = "generate"
data_baseclass = "class Saleae::Graph::Data"

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

index = clang.cindex.Index.create()


def is_class_or_struct(cursor) -> bool:
    # returns true if the cursor is a class or struct.
    return cursor.kind == clang.cindex.CursorKind.CLASS_DECL or cursor.kind == clang.cindex.CursorKind.STRUCT_DECL


def class_extends_data(cursor) -> bool:
    if is_class_or_struct(cursor) == False:
        raise Exception()
    # CursorKind.CXX_BASE_SPECIFIER class Saleae::Graph::Data
    if any([c for c in cursor.get_children() if c.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER and c.spelling == data_baseclass]):
        return True
    return False


def is_class_in_same_file(cursor, current_file_path: str) -> bool:
    if is_class_or_struct(cursor) == False:
        raise Exception()
    if os.path.normpath(cursor.location.file.name) != os.path.normpath(current_file_path):
        # print('rejecting', cursor.location.file, "!=", current_file_path)
        return False
    return True


def is_valid_class_for_cereal(class_, current_file_path: str):
    # checks to see if the cursor is a class or struct, and that it's tagged with the correct attribute.
    if (not is_class_or_struct(class_)):
        return False
    if not is_class_in_same_file(class_, current_file_path):
        return False
    if not any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == annotation_tag]):
        return False
    return True


def is_namespace(ns):
    if ns.kind == clang.cindex.CursorKind.NAMESPACE:
        return True
    return False


def is_valid_namespace_for_cereal(ns, current_file_path: str):
    # checks to see if the cursor is a namespace and that it includes at least one class or struct with the correct attribute.
    if ns.kind != clang.cindex.CursorKind.NAMESPACE:
        return False
    if any([is_valid_class_for_cereal(class_, current_file_path) for class_ in ns.get_children()]):
        return True
    return False


def concatenate_namespaces(base: str, new: str) -> str:
    # helper function to handle adding '::' between namespaces.
    if base == '':
        return new
    return base + '::' + new


def get_namespace_cursors(translation_unit_cursor, current_file_path: str, namespace_path='') -> List[NamespaceCursor]:
    # this extracts the namespace cursor and complete name (including ::) for all namespaces bellow the root.
    # this recursively explores all namespaces.
    # not sure if this will work more than 2 deep. (it does not)
    namespace_cursors: List[NamespaceCursor] = []
    # check for top-level (no-namespaced) classes too!
    if translation_unit_cursor.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        # check for child classes without namespaces:
        if any([is_valid_class_for_cereal(class_, current_file_path) for class_ in translation_unit_cursor.get_children()]):
            new_entry: NamespaceCursor = {'cursor': translation_unit_cursor, 'path': ''}
            namespace_cursors.append(new_entry)

    for child in translation_unit_cursor.get_children():

        if(is_valid_namespace_for_cereal(child, current_file_path)):
            new_entry: NamespaceCursor = {'cursor': child, 'path': concatenate_namespaces(namespace_path, child.spelling)}
            namespace_cursors.append(new_entry)
        if is_namespace(child):
            namespace_cursors.extend(get_namespace_cursors(child, current_file_path, concatenate_namespaces(namespace_path, child.spelling)))
        # if(child.kind == clang.cindex.CursorKind.NAMESPACE and any([is_valid_namespace_for_cereal(grandchild) for grandchild in child.get_children()])):
        #    namespace_cursors.extend(get_namespace_cursors(child, child.spelling))
    return namespace_cursors

# this recursively finds and parses the members of all classes at and below the provided cursor.


def get_args(method) -> List[Arg]:
    # 'json_name': convert_name(arg.spelling)
    return [{'name': arg.spelling, 'type': arg.type.spelling} for arg in method.get_arguments() if arg.kind ==
            clang.cindex.CursorKind.PARM_DECL]


def get_methods(class_) -> List[Method]:
    methods: List[Method] = [{'name': method.spelling, 'return_type': method.result_type.spelling, 'args': get_args(method)}
                             for method in class_.get_children() if method.kind == clang.cindex.CursorKind.CXX_METHOD]
    return methods


def print_cursor(cursor):
    print(cursor.spelling)
    print(cursor.displayname)
    print(cursor.kind)
    print(cursor.location.file)
    print(cursor.translation_unit)
    print("\n\n")


def parse_class(class_, current_file_path: str, path='') -> List[ParsedClass]:
    # parse a class, and any child-classes it may contain
    # print_cursor(class_)
    classes: List[ParsedClass] = []
    members: List[Member] = [{'name': member.spelling, 'json_name': convert_name_for_json(member.spelling), 'ts_type': convert_type_for_ts(member.type.spelling)}
                             for member in class_.get_children() if member.kind == clang.cindex.CursorKind.FIELD_DECL]
    methods: List[Method] = get_methods(class_)
    classes.append({'name': class_.spelling, 'full_name': concatenate_namespaces(path, class_.spelling),
                    'members': members, 'methods': methods, 'extends_data': class_extends_data(class_)})
    for child in class_.get_children():
        if(is_class_or_struct(child)):
            classes.extend(parse_class(child, current_file_path, concatenate_namespaces(path, class_.spelling)))
    return classes


def parse_namespace(ns, current_file_path, path) -> Namespace:
    # classes is now a nested list we need to flatten
    classes = [parse_class(class_, current_file_path) for class_ in ns.get_children() if is_class_or_struct(class_) and is_class_in_same_file(class_, current_file_path) and any(
        [c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == annotation_tag])]

    classes = [class_ for class_list in classes for class_ in class_list]
    return {'name': path, 'classes': classes}


def parse_header(path: str, includes: Set[str]) -> ParsedHeader:
    # parses the heder file for tagged classes and structs.
    original_header_name = os.path.basename(path)

    compiler_options = ['-x', 'c++', '-std=c++17',
                        '-DGENERATE_ARCHIVE=__attribute__((annotate(\"generate\")))', '-D_SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING']+extraCompilerOptions
    compiler_options.extend(["-I" + inc for inc in list(includes)])
    translation_unit = index.parse(path, compiler_options)
    for diag in translation_unit.diagnostics:
        print(diag)
    current_file_path = path
    namespace_cursors = get_namespace_cursors(translation_unit.cursor, current_file_path)
    namespaces = [parse_namespace(ns['cursor'], current_file_path, ns['path']) for ns in namespace_cursors]
    original_header_name = os.path.basename(path)
    if original_header_name == "frame.h":
        print("got it!")
        print(namespaces)
        print(path)
        print(includes)
        # quit()
    return {
        'include': original_header_name,
        'namespaces': namespaces
    }


def header_includes_exports(path: str) -> bool:
    with open(path) as f:
        data = f.read()
    if "GENERATE_ARCHIVE" in data:
        return True
    return False
