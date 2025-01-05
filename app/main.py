import sys
from app.storage import init_git, read_object, write_object

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    match sys.argv[1:]:
        case ['init']:
            init_git()
            return
        case ['cat-file', '-p', hash]:
            _, content = read_object(hash)
            sys.stdout.write(content.decode())
            return
        case ['hash-object', '-w', filename]:
            with open(filename, "rb") as file:
                content = file.read()
            hash = write_object(content, "blob").hex()
            sys.stdout.write(hash)
            return
        case _:
            command = sys.argv[1]
            raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
