
def read_file(filepath: str):
    with open(filepath, "rb") as file:
        return file.read()