import sys
from enum import Enum
from app.storage.object import read_object, write_object

class DeltaInstr(Enum):
    INSERT = 0
    COPY = 1

def decode_size(content: bytes) -> tuple[str, bytes, int]:
    index = 0
    size = (content[0] & 0x7f)
    if (content[0] & 0x80):
        index = 1
        size += content[1] << 7
    return size, index+1

def decode_instruction(content: bytes) -> tuple[tuple, int]:
    type = (content[0] & 0x80) >> 7
    if type == DeltaInstr.INSERT.value:
        delta_size = (content[0] & 0x7f)
        value = content[1:delta_size+1]
        return (DeltaInstr.INSERT, value), delta_size+1

    elif type == DeltaInstr.COPY.value:
        index = 1
        delta_offset = 0
        delta_size = 0
        for i in range(4):
            if content[0] & (0x1 << i):
                delta_offset += content[index] << (8 * i)
                index += 1
        for i in range(3):
            if content[0] & (0x10 << i):
                delta_size += content[index] << (8 * i)
                index += 1
        if delta_size == 0:
            delta_size = 0x10000
        return (DeltaInstr.COPY, delta_offset, delta_size), index

def parse_delta(content: bytes):
    source, index = decode_size(content)
    content = content[index:]
    target, index = decode_size(content[index:])
    content = content[index:]
    print(f"delta {source} {target}", file=sys.stderr)

    instr_list: list[tuple] = []
    while content != b"":
        instr, index = decode_instruction(content)
        instr_list.append(instr)
        content = content[index:]
    return instr_list

def apply_delta(object: str, content: bytes):
    print(f"apply delta on {object}", file=sys.stderr)
    instr_list = parse_delta(content)

    type, source_content = read_object(object)
    target_content = b""
    for instr in instr_list:
        match instr:
            case (DeltaInstr.COPY, offset, size):
                target_content += source_content[offset:offset+size]
            case (DeltaInstr.INSERT, value):
                target_content += value

    write_object(target_content, type)