import hashlib
import os
import sys
import zlib

def read_file(filepath: str):
    with open(filepath, "rb") as file:
        return file.read()

def read_object(hash: str) -> tuple[str, bytes]:
    filename = f".git/objects/{hash[0:2]}/{hash[2:]}"
    with open(filename, "rb") as file:
        compressed = file.read()
    object = zlib.decompress(compressed)

    header, content = object.split(b"\0", 1)
    type, size = header.decode().split(" ", 1)
    print(f"object read {type} {size} {hash}", file=sys.stderr)
    return type, content[:int(size)]

def write_object(content: bytes, type: str) -> bytes:
    header = f"{type} {len(content)}\0".encode()
    object = header + content
    compressed = zlib.compress(object)

    hash_sha1 = hashlib.sha1(object).digest()
    hex = hash_sha1.hex()
    filename = f".git/objects/{hex[0:2]}/{hex[2:]}"
    os.makedirs(f".git/objects/{hex[0:2]}", exist_ok=True)

    with open(filename, "wb") as file:
        file.write(compressed)
    print(f"object write {type} {len(content)} {hex}", file=sys.stderr)
    return hash_sha1