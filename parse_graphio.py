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

    parts = path.parts
    if parts[-2] != "src":
        return False
    if parts[-5] != "graph-io":
        return False
    category = parts[-4]
    if not category in allowed_categorys:
        return False
    return True


def get_target(entry: CompileCommand) -> str:
    if not is_public_src_file(entry):
        raise Exception()
    path = Path(entry['file'])
#    return os.path.join(path.parts[:-2].)
    return "{}\\{}".format(path.parts[-4], path.parts[-3])


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
        headers = [os.path.join(public_include_folder, f) for f in os.listdir(public_include_folder) if os.path.isfile(os.path.join(public_include_folder, f)) and Path(os.path.join(public_include_folder, f)).suffix == ".h"
                   ]
        for include in headers:
            all_headers[include] = includes_lookup[target]
    return all_headers


def parse_compile_commands(compile_commands_path: str) -> List[CompileCommand]:
    with open(compile_commands_path) as f:
        return json.load(f)
