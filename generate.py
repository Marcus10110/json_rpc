#!/usr/bin/env python
import pprint
import os
from parse_header import parse_header

from mako.template import Template
# from name_convert import convert_name, convert_type

headerFiles = ['native/src/render_data.h']

# helper to manually load file before passing to mako, to fix the line ending problems on windows.


def load_template(filename):
    with open(filename) as f:
        template_str = f.read()
    template = Template(template_str)
    return template


# loop through all provided headerFiles and generate json code for them.


archive_header_template = load_template('archive_header.mako')
archive_src_template = load_template('archive_source.mako')
archive_ts_template = load_template('cereal_ts.mako')

for header in headerFiles:
    header_data = parse_header(header)
    pprint.pprint(header_data)

    # generate a header file!
    if(len(header_data['namespaces']) == 0):
        print('no GENERATE_CEREAL classes found in ' + header)
        continue

    generated_header_path = os.path.splitext(header)[0] + '.gen2.h'
    generated_src_path = os.path.splitext(header)[0] + '.gen2.cpp'
    generated_ts_path = os.path.splitext(header)[0] + '.gen2.ts'
    generated_include = os.path.basename(generated_header_path)
    print(generated_header_path, generated_src_path, generated_include)

    generated_header_content = archive_header_template.render(params=header_data)
    print(generated_header_content)
    generated_src_content = archive_src_template.render(params=header_data, generated_include=generated_include)
    print(generated_src_content)
    generated_ts_content = archive_ts_template.render(params=header_data)
    print(generated_ts_content)

    generated_header_file = open(generated_header_path, "w")
    n = generated_header_file.write(generated_header_content)
    generated_header_file.close()

    generated_src_file = open(generated_src_path, "w")
    n = generated_src_file.write(generated_src_content)
    generated_src_file.close()

    generated_ts_file = open(generated_ts_path, "w")
    n = generated_ts_file.write(generated_ts_content)
    generated_ts_file.close()
