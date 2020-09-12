#!/usr/bin/env python
from io import StringIO
import os
import platform
import sys
import clang.cindex
from typing import List, Dict, Tuple, Sequence, TypedDict, Any, NamedTuple
from name_convert import convert_name_for_json, convert_type_for_ts


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


class Namespace(TypedDict):
    name: str
    classes: List[ParsedClass]


class ParsedHeader(TypedDict):
    include: str
    namespaces: List[Namespace]


annotation_tag = "generate"

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


def is_valid_class_for_cereal(class_):
    # checks to see if the cursor is a class or struct, and that it's tagged with the correct attribute.
    if (not is_class_or_struct(class_)):
        return False
    if not any([c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == annotation_tag]):
        return False
    return True


def is_valid_namespace_for_cereal(ns):
    # checks to see if the cursor is a namespace and that it includes at least one class or struct with the correct attribute.
    if ns.kind != clang.cindex.CursorKind.NAMESPACE:
        return False
    if any([is_valid_class_for_cereal(class_) for class_ in ns.get_children()]):
        return True
    return False


def concatenate_namespaces(base: str, new: str) -> str:
    # helper function to handle adding '::' between namespaces.
    if base == '':
        return new
    return base + '::' + new


def get_namespace_cursors(translation_unit_cursor, namespace_path='') -> List[NamespaceCursor]:
    # this extracts the namespace cursor and complete name (including ::) for all namespaces bellow the root.
    # this recursively explores all namespaces.
    # not sure if this will work more than 2 deep.
    namespace_cursors: List[NamespaceCursor] = []
    for child in translation_unit_cursor.get_children():
        if(is_valid_namespace_for_cereal(child)):
            new_entry: NamespaceCursor = {'cursor': child, 'path': concatenate_namespaces(namespace_path, child.spelling)}
            namespace_cursors.append(new_entry)
        if(child.kind == clang.cindex.CursorKind.NAMESPACE and any([is_valid_namespace_for_cereal(grandchild) for grandchild in child.get_children()])):
            namespace_cursors.extend(get_namespace_cursors(child, child.spelling))
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


def parse_class(class_, path='') -> List[ParsedClass]:
    # parse a class, and any child-classes it may contain
    classes: List[ParsedClass] = []
    members: List[Member] = [{'name': member.spelling, 'json_name': convert_name_for_json(member.spelling), 'ts_type': convert_type_for_ts(member.type.spelling)}
                             for member in class_.get_children() if member.kind == clang.cindex.CursorKind.FIELD_DECL]
    methods: List[Method] = get_methods(class_)
    classes.append({'name': class_.spelling, 'full_name': concatenate_namespaces(path, class_.spelling), 'members': members, 'methods': methods})
    for child in class_.get_children():
        if(is_class_or_struct(child)):
            classes.extend(parse_class(child, concatenate_namespaces(path, class_.spelling)))
    return classes


def parse_namespace(ns, path) -> Namespace:
    # classes is now a nested list we need to flatten
    classes = [parse_class(class_) for class_ in ns.get_children() if is_class_or_struct(class_) and any(
        [c for c in class_.get_children() if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR and c.spelling == annotation_tag])]

    classes = [class_ for class_list in classes for class_ in class_list]
    return {'name': path, 'classes': classes}


def parse_header(path: str) -> ParsedHeader:
    # parses the heder file for tagged classes and structs.
    original_header_name = os.path.basename(path)
    translation_unit = index.parse(path, ['-x', 'c++', '-std=c++17', '-D__CODE_GENERATOR__']+extraCompilerOptions)
    for diag in translation_unit.diagnostics:
        print(diag)
    namespace_cursors = get_namespace_cursors(translation_unit.cursor)
    namespaces = [parse_namespace(ns['cursor'], ns['path']) for ns in namespace_cursors]
    original_header_name = os.path.basename(path)

    return {
        'include': original_header_name,
        'namespaces': namespaces
    }
