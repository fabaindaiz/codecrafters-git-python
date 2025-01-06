import sys
from app.storage.object import read_file, write_file, read_object, write_object

# Commands
def cat_file(p: str):
    type, content = read_object(p)
    if type != "blob":
        raise ValueError(f"{p} is not a blob object")
    sys.stdout.write(content.decode())

def hash_object(w: str):
    content = read_file(w)
    hash = write_object(content, "blob").hex()
    sys.stdout.write(hash)


def restore_blob(filepath: str, hash: str):
    type, content = read_object(hash)
    if type != "blob":
        raise ValueError(f"{hash} is not a blob object")
    print(f"restore blob {hash} to {filepath}", file=sys.stderr)
    write_file(filepath, content)