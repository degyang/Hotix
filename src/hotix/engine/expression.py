import re

_INDEX_ID_PATTERN = re.compile(r"\bindex\.([0-9][A-Za-z0-9_]*)")
_PAIR_ID_PATTERN = re.compile(r"\bpair\.([0-9][A-Za-z0-9_]*)")


def normalize_expression(expr: str) -> str:
    expr = _INDEX_ID_PATTERN.sub(r'index["\1"]', expr)
    expr = _PAIR_ID_PATTERN.sub(r'pair["\1"]', expr)
    return expr


class _PathNode:
    def __init__(self, prefix: str, resolver):
        self.prefix = prefix
        self.resolver = resolver

    def __getattr__(self, name: str):
        return self.resolver.resolve(f"{self.prefix}.{name}")


class _CollectionNode:
    def __init__(self, head: str, resolver):
        self.head = head
        self.resolver = resolver

    def __getattr__(self, name: str):
        return _PathNode(f"{self.head}.{name}", self.resolver)

    def __getitem__(self, key: str):
        return _PathNode(f"{self.head}.{key}", self.resolver)


def evaluate_expression(expr: str, resolver, rule_id: str = ""):
    local_env = {
        "__builtins__": {},
        "abs": abs,
        "max": max,
        "min": min,
        "len": len,
        "self": type(
            "Obj", (), {"__getattr__": lambda _, name: resolver.resolve(f"self.{name}")}
        )(),
        "prev": type(
            "Obj", (), {"__getattr__": lambda _, name: resolver.resolve(f"prev.{name}")}
        )(),
        "left": type(
            "Obj", (), {"__getattr__": lambda _, name: resolver.resolve(f"left.{name}")}
        )(),
        "right": type(
            "Obj",
            (),
            {"__getattr__": lambda _, name: resolver.resolve(f"right.{name}")},
        )(),
        "index": _CollectionNode("index", resolver),
        "pair": _CollectionNode("pair", resolver),
        "market": type(
            "Obj",
            (),
            {"__getattr__": lambda _, name: resolver.resolve(f"market.{name}")},
        )(),
        "true": True,
        "false": False,
    }
    return eval(normalize_expression(expr), local_env, {})  # noqa: S307
