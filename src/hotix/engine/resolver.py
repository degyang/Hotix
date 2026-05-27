from types import SimpleNamespace


def _wrap_value(value):
    if isinstance(value, dict):
        return SimpleNamespace(
            **{key: _wrap_value(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return [_wrap_value(item) for item in value]
    return value


class Resolver:
    def __init__(self, current=None, prev=None, indices=None, pairs=None, market=None):
        self.current = current
        self.prev = prev
        self.indices = indices or {}
        self.pairs = pairs or {}
        self.market = market

    def resolve(self, ref: str):
        head, _, tail = ref.partition(".")
        if head == "self":
            return self.current.get_field(tail)
        if head == "prev":
            return self.prev.get_field(tail)
        if head == "left":
            return self.indices[self.current.left].get_field(tail)
        if head == "right":
            return self.indices[self.current.right].get_field(tail)
        if head == "index":
            index_id, _, field_name = tail.partition(".")
            return self.indices[index_id].get_field(field_name)
        if head == "pair":
            pair_id, _, field_name = tail.partition(".")
            return self.pairs[pair_id].get_field(field_name)
        if head == "market":
            value = self.market
            for part in tail.split("."):
                if isinstance(value, dict):
                    value = value[part]
                else:
                    value = getattr(value, part)
            return _wrap_value(value)
        raise KeyError(ref)
