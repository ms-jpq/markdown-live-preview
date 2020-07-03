from xmltodict import parse, unparse


def reconciliate(prev: str, curr: str) -> str:
    tree = parse(prev)
    out = unparse(tree)
    return out
