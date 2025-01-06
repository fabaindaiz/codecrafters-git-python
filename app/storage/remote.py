import hashlib
import sys
import os
import zlib
import requests
from app.object.delta import apply_delta
from app.object.commit import restore_commit
from app.storage.folder import git_init
from app.storage.object import read_file, write_file, write_object

# Commands
def git_clone(repository: str, folder: str):
    clone_init(folder)
    git_init()
    head, branches = get_refs(repository)
    pack = get_pack(repository, [head], [])
    unpack_pack(pack)
    print("# ----------------------------------------", file=sys.stderr)
    restore_commit(head)

def clone_init(folder: str):
    os.makedirs(folder, exist_ok=True)
    os.chdir(folder)

def get_refs(repository: str):
    refs_url = f"{repository}/info/refs?service=git-upload-pack"
    refs = requests.get(refs_url).text
    refs_lines = refs.split("\n")

    service = refs_lines[0]
    head, capability = refs_lines[1].split(" ", 1)
    references = refs_lines[2:-1]

    branches: dict[str, str] = {}
    for branch in references:
        object, name = branch.split(" ", 1)
        branches[name] = object[-40:]

    print(f"refs {head[-40:]} {branches}", file=sys.stderr)
    return head[-40:], branches

HAVE_SEP = b"0000"
PACK_DONE = b"0009done\n"

def decode_type(type: int):
    if type == 1:
        return "commit"
    elif type == 2:
        return "tree"
    elif type == 3:
        return "blob"
    elif type == 4:
        return "tag"
    elif type == 6:
        return "ofs-delta"
    elif type == 7:
        return "ref-delta"
    else:
        return "unknown"

def decode_object(pack: bytes) -> tuple[str, bytes, int]:
    index = 0
    type = (pack[index] >> 4) & 7
    size = (pack[index] & 15)
    while (pack[index] & 0x80):
        index += 1
        size += (pack[index] & 0x7f) << (4 + (7 * (index - 1)))
    return decode_type(type), index+1, size

def get_pack(repository: str, want: list[str], have: list[str]):
    pack_url = f"{repository}/git-upload-pack"
    want_str = "".join(f"0032want {object}\n" for object in want).encode()
    have_str = "".join(f"0032have {object}\n" for object in have).encode()

    request_data = want_str + HAVE_SEP + have_str + PACK_DONE
    print(f"pack request {request_data}", file=sys.stderr)
    pack = requests.post(pack_url, data=request_data.lstrip())
    acks, package = pack.content.split(b"0008NAK\n", 1)

    pack_headers = package[:12]
    pack_objects = package[12:-20]
    content = pack_headers + pack_objects

    pack_checksum = package[-20:]

    num_objects = int.from_bytes(pack_headers[8:12], "big")
    print(f"pack with {num_objects} objects", file=sys.stderr)

    digest = hashlib.sha1(content).digest()
    if pack_checksum != digest:
        raise ValueError("Pack checksum error")
    
    os.makedirs(".git/objects/pack", exist_ok=True)
    filepath = f".git/objects/pack/pack-{digest.hex()}.pack"
    write_file(filepath, content)
    return digest.hex()
    
def unpack_pack(package: bytes) -> list[str]:
    filepath = f".git/objects/pack/pack-{package}.pack"
    pack = read_file(filepath)

    pack_headers = pack[:12]
    pack_objects = pack[12:]

    num_objects = int.from_bytes(pack_headers[8:12], "big")
    size_objects = len(pack_objects)
    objects_hash: list[str] = []

    absolute_index = 0
    while pack_objects != b"":
        type, index, _ = decode_object(pack_objects)

        if type == "ofs-delta":
            raise NotImplementedError()
        elif type == "ref-delta":
            object = pack_objects[index:index+20].hex()
            content = zlib.decompress(pack_objects[index+20:])
            apply_delta(object, content)

            index = len(zlib.compress(content)) + index +20
        else:
            content = zlib.decompress(pack_objects[index:])
            hash = write_object(content, type).hex()
            objects_hash.append(hash)

            index = len(zlib.compress(content)) + index

        print(f"pack {type} ({index}) [{absolute_index}/{size_objects}]", file=sys.stderr)
        pack_objects = pack_objects[index:]
        absolute_index += index

    return objects_hash