import os

# Commands
def git_init():
    if os.path.exists(".git"):
        raise FileExistsError("This is already a git repository")
    init_repository()


def init_repository():
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")