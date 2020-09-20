#!/usr/bin/env python
import os
import pprint

from mako.template import Template

from parse_graphio import get_libclang_inputs, parse_compile_commands
from parse_header import header_includes_exports, parse_header

# Set path to graph-io repository root and set path to compile_commands.json
repo_root = "C:\\Users\\Mark\\Software\\graph-io"
build_dir = os.path.join(repo_root, "build", "win64")
compile_commands_path = os.path.join(build_dir, "compile_commands.json")


compile_commands = parse_compile_commands(compile_commands_path)
libclang_inputs = get_libclang_inputs(compile_commands, repo_root)

# use this to test the render_data.h file that's included.
# libclang_inputs = {
#    "native/src/render_data.h": set()
# }


def load_template(filename):
    with open(filename) as f:
        template_str = f.read()
    template = Template(template_str)
    return template


# load the mako templates.
archive_header_template = load_template('archive_header.mako')
archive_src_template = load_template('archive_source.mako')
archive_ts_template = load_template('cereal_ts.mako')


count = 0

for header, includes in libclang_inputs.items():
    if header_includes_exports(header) == False:
        continue
    header_data = parse_header(header, includes)
    pprint.pprint(header_data)
#    quit()
    count += 1
    if count > 10:
        quit
    # continue
    # quit()
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
