import sys
from app.objects.tree import parse_tree, create_tree
from app.storage import init_git, read_object, write_object
from app.util import read_file

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    match sys.argv[1:]:
        case ['init']:
            init_git()
            return
        case ['cat-file', '-p', hash]:
            type, content = read_object(hash)
            sys.stdout.write(content.decode())
            return
        case ['hash-object', '-w', filepath]:
            content = read_file(filepath)
            hash = write_object(content, "blob").hex()
            sys.stdout.write(hash)
            return
        case ['ls-tree', '--name-only', hash]:
            type, content = read_object(hash)
            tree_str = parse_tree(content)
            sys.stdout.write(tree_str)
            return
        case ['write-tree']:
            hash = create_tree(".").hex()
            sys.stdout.write(hash)
            return
        case _:
            command = sys.argv[1]
            raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
