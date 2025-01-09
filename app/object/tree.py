import os
import sys
from app.object.blob import restore_blob
from app.storage.object import read_file, read_object, write_object

# Commands
def ls_tree(tree_sha: str, name_only: bool = False):
    type, content = read_object(tree_sha)
    if type != "tree":
        raise ValueError(f"{tree_sha} is not a tree object")
    tree_items = parse_tree(content)

    if name_only:
        tree_str = "".join(f"{item[2]}\n" for item in tree_items)
    else:
        tree_str = "".join(f"{item[0]} type {item[1]}    {item[2]}\n" for item in tree_items)
    sys.stdout.write(tree_str)

def write_tree():
    hash = create_tree(".").hex()
    sys.stdout.write(hash)


def decode_mode(mode: str) -> str:
    if mode.startswith("100"):
        return "blob", int(mode[3:])
    elif mode.startswith("40"):
        return "tree", int(mode[2:])
    else:
        raise ValueError(f"Unknown mode {mode}")

def parse_tree(content: bytes) -> list[tuple[int, str, str]]:
    tree_items: list[tuple[int, bytes, str]] = []
    while content != b"":
        stat, content = content.split(b"\0", 1)
        mode, name = stat.decode().split(" ", 1)
        object = content[:20].hex()
        content = content[20:]

        tree_items.append((mode, object, name))
    return tree_items

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
            mode = oct(os.stat(path).st_mode).removeprefix("0o")
        elif os.path.isdir(path):
            digest = create_tree(path)
            mode = "40000"
        entry = f"{mode} {name}\0".encode() + digest
        tree.update({name: entry})

    tree = dict(sorted(tree.items(), key=lambda item: item[0]))
    content = b"".join(tree.values())
    return write_object(content, type="tree")


def restore_case(type: str, filepath: str, hash: str, perms: int):
    type, _ = read_object(hash)
    if type == "tree":
        os.makedirs(filepath, exist_ok=True)
        restore_tree(filepath, hash)
    elif type == "blob":
        restore_blob(filepath, hash)
        os.chmod(filepath, perms)
    else:
        raise ValueError(f"{hash} is not a tree or blob object")

def restore_tree(path: str, hash: str):
    type, content = read_object(hash)
    if type != "tree":
        raise ValueError(f"{hash} is not a tree object")
    
    print(f"restore tree {hash} to {path}", file=sys.stderr)
    tree_items = parse_tree(content)
    for mode, object, name in tree_items:

        type, perms = decode_mode(mode)
        filepath = os.path.join(path, name)
        restore_case(type, filepath, object, perms)