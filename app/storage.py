import hashlib
import os
import zlib

def init_git():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")

def read_object(hash: str) -> tuple[str, bytes]:
    filename = f".git/objects/{hash[0:2]}/{hash[2:]}"
    with open(filename, "rb") as file:
        compressed = file.read()
    object = zlib.decompress(compressed)
    header, content = object.split(b"\0", 1)
    
    type, size = header.decode().split(" ", 1)
    return type, content[:int(size)]

def write_object(content: bytes, type: str) -> bytes:
    header = f"{type} {len(content)}\0".encode()
    object = header + content
    hash_sha1 = hashlib.sha1(object)

    hash = hash_sha1.hexdigest()
    os.makedirs(f".git/objects/{hash[0:2]}", exist_ok=True)

    compressed = zlib.compress(object)
    filename = f".git/objects/{hash[0:2]}/{hash[2:]}"
    with open(filename, "wb") as file:
        file.write(compressed)
    
    return hash_sha1.digest()
