import sys
from app.object.blob import cat_file, hash_object
from app.object.tree import ls_tree, write_tree
from app.object.commit import commit_tree
from app.storage.folder import git_init
from app.parse import parse_argv

def main():
    command, args, kwargs = parse_argv(sys.argv[1:])
    match command:
        case 'init':
            git_init()
        case 'cat-file':
            cat_file(*args, **kwargs)
        case 'hash-object':
            hash_object(*args, **kwargs)
        case 'ls-tree':
            ls_tree(*args, **kwargs)
        case 'write-tree':
            write_tree(*args, **kwargs)
        case 'commit-tree':
            commit_tree(*args, **kwargs)
        case _:
            raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()