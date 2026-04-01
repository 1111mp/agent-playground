def read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def write_file(absolutePath: str, content: str) -> str:
    with open(absolutePath, "w") as f:
        f.write(content)
    return "write success"
