import os
import sys
from app.storage.object import read_file, read_object, write_object

# Commands
def ls_tree(tree_sha: str, name_only: bool = False):
    type, content = read_object(tree_sha)
    if type != "tree":
        raise ValueError(f"{tree_sha} is not a tree object")
    tree_str = parse_tree(content, name_only=name_only)
    sys.stdout.write(tree_str)

def write_tree():
    hash = create_tree(".").hex()
    sys.stdout.write(hash)


def parse_tree(content: bytes, name_only: bool = False) -> str:
    tree_str = ""
    while content != b"":
        stat, content = content.split(b"\0", 1)
        mode, name = stat.decode().split(" ", 1)
        object = content[:20].hex()

        if name_only:
            tree_str += f"{name}\n"
        else:
            tree_str += f"{mode} type {object}    {name}"
        content = content[20:]
    return tree_str

def create_tree(folder: str):
    tree: dict[str, str] = {}
    for finded in os.listdir(folder):
        path = f"{folder}/{finded}"
        name = os.path.basename(path)
        if name == ".git":
            continue
        elif os.path.isfile(path):
            content = read_file(path)
            digest = write_object(content, type="blob")
            mode = "100644"
        elif os.path.isdir(path):
            digest = create_tree(path)
            mode = "40000"
        entry = f"{mode} {name}\0".encode() + digest
        tree.update({name: entry})

    tree = dict(sorted(tree.items(), key=lambda item: item[0]))
    content = b"".join(tree.values())
    return write_object(content, type="tree")