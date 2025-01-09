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
    head, branches, main = get_refs(repository)
    want = [head] + list(branches.values()) #, head]

    pack = get_pack(repository, want=want)
    unpack_pack(repository, pack)

    print("# ----------------------------------------", file=sys.stderr)
    restore_commit(head)


def clone_init(folder: str):
    os.makedirs(folder, exist_ok=True)
    os.chdir(folder)

def get_refs(repository: str, type: str = "heads", main_branch: str = "refs/heads/master"): # ["heads", "pull", "tags"]
    refs_url = f"{repository}/info/refs?service=git-upload-pack"
    refs = requests.get(refs_url).text
    refs_lines = refs.split("\n")

    service = refs_lines[0]
    head, capability = refs_lines[1].split(" ", 1)
    for cap in capability.split(" "):
        if cap.startswith("symref="):
            main_branch = cap.split(":", 1)[1]
    references = refs_lines[2:-1]

    branches: dict[str, str] = {}
    for branch in references:
        object, name = branch.split(" ", 1)
        if name.startswith(f"refs/{type}"):
            branches[name] = object[-40:]

    print(f"refs {head[-40:]} {branches}", file=sys.stderr)
    return head[-40:], branches, main_branch

HAVE_SEP = b"0000"
PACK_DONE = b"0009done\n"

def get_pack(repository: str, want: list[str], have: list[str] = []):
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
    digest = hashlib.sha1(content).digest()
    if pack_checksum != digest:
        raise ValueError("Pack checksum error")
    
    os.makedirs(".git/objects/pack", exist_ok=True)
    filepath = f".git/objects/pack/pack-{digest.hex()}.pack"
    write_file(filepath, content)
    return digest.hex()

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
    while (pack[index] & 0x80) and index < 10:
        index += 1
        size += (pack[index] & 0x7f) << (4 + (7 * (index - 1)))
    return decode_type(type), index+1, size

def unpack_pack(repository: str, package: bytes) -> list[str]:
    filepath = f".git/objects/pack/pack-{package}.pack"
    pack = read_file(filepath)

    pack_headers = pack[:12]
    pack_objects = pack[12:]

    size_objects = len(pack_objects)
    num_objects = int.from_bytes(pack_headers[8:12], "big")
    print(f"pack with {num_objects} objects", file=sys.stderr)

    absolute_index = 0
    while pack_objects != b"":
        type, object_start, size = decode_object(pack_objects)

        try:
            match type:
                case "ref-delta":
                    content = zlib.decompress(pack_objects[object_start+20:])
                    object_end = len(zlib.compress(content)) + object_start + 20
                    if len(content) != size:
                        raise ValueError(f"Delta size error {len(content)} != {size}")

                    object_hex = pack_objects[object_start:object_start+20].hex()
                    try:
                        apply_delta(object_hex, content)
                    except:
                        pack_hex = get_pack(repository, want=[object_hex])
                        unpack_pack(repository, pack_hex)
                        apply_delta(object_hex, content)

                case "commit" | "tree" | "blob" | "tag":
                    content = zlib.decompress(pack_objects[object_start:])
                    object_end = len(zlib.compress(content)) + object_start
                    if len(content) != size:
                        raise ValueError(f"Delta size error {len(content)} != {size}")
                        
                    write_object(content, type)
                
                case _:
                    pack_objects = pack_objects[1:]
                    absolute_index += 1
                    continue
    
        # except zlib.error as e:
        #     pack_objects = pack_objects[1:]
        #     absolute_index += 1
        #     continue

        # except ValueError as e:
        #     pack_objects = pack_objects[object_end:]
        #     absolute_index += object_end

        except:
            raise Exception(f"Cloning multi branch repositories is not supported yet")

        print(f"pack {type} ({size}) [{absolute_index}/{size_objects}]", file=sys.stderr)
        pack_objects = pack_objects[object_end:]
        absolute_index += object_end