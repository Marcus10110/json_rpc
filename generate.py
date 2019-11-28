#!/usr/bin/env python
""" Usage: call with <filename>
"""
import os
import sys
import clang.cindex

from mako.template import Template

clang.cindex.Config.set_library_file(
    '/usr/local/Cellar/llvm/9.0.0_1/lib/libclang.dylib')

headerFiles = ['native/src/server.h']


def findClasses(root):
    # ensure we're at the top of a file.
    if(root.kind != clang.cindex.CursorKind.TRANSLATION_UNIT):
        return
    namespaces = filter(lambda node: node.kind ==
                        clang.cindex.CursorKind.NAMESPACE, root.get_children())
    classes = []
    for namespace in namespaces:
        for child in namespace.get_children():
            if child.kind == clang.cindex.CursorKind.CLASS_DECL:
                if any([c for c in child.get_children()
                        if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR]):
                    classes.append(child)

    return classes


def processClass(klass):
    methodCursors = [c for c in klass.get_children()
                     if c.kind == clang.cindex.CursorKind.CXX_METHOD]

    methods = []
    for method in methodCursors:
        name = method.spelling
        returnType = method.result_type.spelling
        args = [{'name': arg.spelling, 'type': arg.type.spelling} for arg in method.get_arguments() if arg.kind ==
                clang.cindex.CursorKind.PARM_DECL]
        print(returnType, name, args)
        methods.append(
            dict({'returnType': returnType, 'name': name, 'args': args}))
    print(methods)
    return methods


tpl = Template(filename='template.mako')

index = clang.cindex.Index.create()
for header in headerFiles:
    tu = index.parse(
        header, ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__', "-I/usr/local/Cellar/llvm/9.0.0_1/include/c++/v1"])
    print('Translation unit:', tu.spelling)
    # find_typerefs(tu.cursor, 0)
    classes = findClasses(tu.cursor)
    methods = []
    for klass in classes:
        methods = methods + processClass(klass)
    generatedContents = tpl.render(methods=methods)
    newFilePath = os.path.splitext(header)[0] + '.gen.h'
    print(newFilePath)
    text_file = open(newFilePath, "w")
    n = text_file.write(generatedContents)
    text_file.close()
