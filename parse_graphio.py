from genericpath import exists
import json
from typing import List, Dict, Tuple, Sequence, TypedDict, Any, NamedTuple, Set
from pathlib import Path
import os
import shlex


class CompileCommand(TypedDict):
    directory: str
    command: str
    file: str


def get_includes(entry: CompileCommand) -> List[str]:
    commands = shlex.split(entry['command'])
    includes = []
    for index, content in enumerate(commands):
        if index < len(commands)-1 and content == "-isystem":
            path = Path(commands[index+1])
            drive, discard = os.path.splitdrive(commands[index+1])
            # filter out relative paths, by removing anything that doesn't start with a drive letter. this won't work on linux/mac
            if drive != None and len(drive) > 0:
                includes.append(commands[index+1])
    return includes


allowed_categorys = ["nodes", "core", "server"]


def is_public_src_file(entry: CompileCommand) -> bool:
    path = Path(entry['file'])
    # handle C:\Users\Mark\Software\graph-io\core\protocol_analyzer\src\protocol_analyzer too
    parts = path.parts
    if "src" in parts and "graph-io" in parts and any([category in parts for category in allowed_categorys]):
        return True
    return False


def get_target(entry: CompileCommand) -> str:
    if not is_public_src_file(entry):
        raise Exception()
    path = Path(entry['file']).parts
    root_index = path.index("graph-io")
    return "{}\\{}".format(path[root_index+1], path[root_index+2])
#    return os.path.join(path.parts[:-2].)
    # return "{}\\{}".format(path.parts[-4], path.parts[-3])


# for every target, collect all include directories. (absolute only)
def get_includes_for_all_targets(data: List[CompileCommand]) -> Dict[str, Set[str]]:
    targets: Dict[str, Set[str]] = dict()
    for i, entry in enumerate(data):
        if not is_public_src_file(entry):
            continue
        target = get_target(entry)
        if not target in targets:
            targets[target] = set()
        targets[target].update(set(get_includes(entry)))
    return targets


# server/graph_python
def get_include_dir_for_target(target: str, repo_root: str) -> str:
    return os.path.join(repo_root, target, "include")


def get_libclang_inputs(data: List[CompileCommand], repo_root: str) -> Dict[str, Set[str]]:
    includes_lookup = get_includes_for_all_targets(data)
    all_targets = includes_lookup.keys()
    all_headers: Dict[str, Set[str]] = dict()
    for target in all_targets:
        public_include_folder = get_include_dir_for_target(target, repo_root)
        if not os.path.exists(public_include_folder):
            continue
        include_dir_contents = os.listdir(public_include_folder)
        headers = []
        headers = [os.path.join(public_include_folder, f) for f in include_dir_contents if os.path.isfile(os.path.join(public_include_folder, f)) and Path(os.path.join(public_include_folder, f)).suffix == ".h"
                   ]
        # snag nested headers
        for item in include_dir_contents:
            full_path = os.path.join(public_include_folder, item)
            if os.path.isfile(full_path) and Path(full_path).suffix == ".h":
                headers.append(full_path)
            if os.path.isdir(full_path):
                # TODO: allow complete recursion
                nested_dir_contents = os.listdir(full_path)
                headers.extend([os.path.join(full_path, f) for f in nested_dir_contents if os.path.isfile(
                    os.path.join(full_path, f)) and Path(os.path.join(full_path, f)).suffix == ".h"])
        for include in headers:
            all_headers[include] = includes_lookup[target]
    return all_headers


def parse_compile_commands(compile_commands_path: str) -> List[CompileCommand]:
    with open(compile_commands_path) as f:
        return json.load(f)
