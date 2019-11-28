#!/usr/bin/env python
""" Usage: call with <filename>
"""

import sys
import clang.cindex


0

def find_typerefs(node, level):

    print(level, node.displayname, node.spelling, node.kind, node.location.file)
    #print('new iteration...')
    #print('kind: ' , node.kind)
    #print('spelling: ' , node.spelling)
    #print('location: ' , node.location)
    #print('is_definition: ' , node.is_definition())

    #if node.is_definition():
    #    print('get_definition spelling: ', node.get_definition().spelling)
    # Recurse for children of this node
    if level < 1:
        for c in node.get_children():
            find_typerefs(c, level+1)
    #print('done with children')

index = clang.cindex.Index.create()
tu = index.parse(sys.argv[1], ['-x', 'c++', '-std=c++11'])
print( 'Translation unit:', tu.spelling)
find_typerefs(tu.cursor, 0)