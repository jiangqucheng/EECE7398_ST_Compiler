import os
import json
from briltxt import parse_bril


def bril2json(bril_in_txt: str, include_pos=False) -> dict:
    """Parse a Bril program from Bril in txt and return a Python Dict.
    Optionally include source position information.
    """
    return json.loads(parse_bril(bril_in_txt, include_pos=include_pos))

def load_bril(filename: str, include_pos=False) -> dict:
    """Load a Bril program from a file and return a Python Dict.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found")
    with open(filename, 'r', encoding="utf-8") as f:
        return bril2json(f.read(), include_pos=include_pos)
