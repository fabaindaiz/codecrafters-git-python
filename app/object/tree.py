import os
from app.storage import write_object
from app.util import read_file

def parse_tree(content: bytes) -> str:
    tree_str = ""
    while content != b"":
        stat, content = content.split(b"\0", 1)
        mode, name = stat.decode().split(" ", 1)
        #object = content[:20].decode()

        tree_str += f"{name}\n"
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