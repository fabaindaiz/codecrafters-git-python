import sys
import os
import requests

# Commands
def git_clone(repository: str, folder: str):
    clone_init(folder)
    get_refs(repository)


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
        branches[name] = object

    print(f"refs {head[-40:]} {branches}", file=sys.stderr)
    return head[-40:], branches