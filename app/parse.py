
def parse_tree(content: bytes) -> str:
    tree_str = ""
    while content != b"":
        stat, content = content.split(b"\0", 1)
        mode, name = stat.decode().split(" ", 1)
        #object = content[:20].decode()

        tree_str += f"{name}\n"
        content = content[20:]
    return tree_str