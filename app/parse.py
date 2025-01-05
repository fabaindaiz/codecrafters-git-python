import sys
from typing import Optional

def parse_argv(argv: list[str]):
    command = argv[0]
    args : list[str] = []
    kwargs : dict[str, str] = {}

    has_flag: Optional[str] = None
    for arg in argv[1:]:
        if arg.startswith("--"):
            arg = arg.removeprefix("--").replace("-", "_")
            kwargs[arg] = True
        elif arg.startswith("-"):
            if has_flag:
                kwargs[has_flag] = True
            has_flag = arg.removeprefix("-").replace("-", "_")
        elif has_flag:
            kwargs[has_flag] = arg
            has_flag = None
        else:
            args.append(arg)
    if has_flag:
        kwargs[has_flag] = True

    print(command, args, kwargs, file=sys.stderr)
    return command, args, kwargs