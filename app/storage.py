import os
import zlib

def init_git():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

def read_object(hash: str) ->tuple[str, bytes]:
    filename = f".git/objects/{hash[0:2]}/{hash[2:]}"
    with open(filename, "rb") as file:
        compressed = file.read()
    object = zlib.decompress(compressed)
    header, content = object.split(b"\0", 1)

    type, size = header.split(b" ", 1)
    return type.decode(), content[:int(size.decode())]
