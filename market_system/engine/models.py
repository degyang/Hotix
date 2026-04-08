from dataclasses import dataclass, field


@dataclass
class IndexRuntime:
    id: str
    date: str
    raw: dict = field(default_factory=dict)
    features: dict = field(default_factory=dict)
    states: dict = field(default_factory=dict)
    pattern_tags: list[str] = field(default_factory=list)
    transition_tags: list[str] = field(default_factory=list)
    salience: dict = field(default_factory=dict)
    trace: dict = field(default_factory=dict)

    def get_field(self, name: str):
        if name in self.raw:
            return self.raw[name]
        if name in self.features:
            return self.features[name]
        if name in self.states:
            return self.states[name]
        if name == "pattern_tags":
            return self.pattern_tags
        if name == "transition_tags":
            return self.transition_tags
        raise KeyError(name)


@dataclass
class PairRuntime:
    id: str
    date: str
    left: str
    right: str
    features: dict = field(default_factory=dict)
    states: dict = field(default_factory=dict)
    relation_tags: list[str] = field(default_factory=list)
    trace: dict = field(default_factory=dict)

    def get_field(self, name: str):
        if name in self.features:
            return self.features[name]
        if name in self.states:
            return self.states[name]
        if name == "relation_tags":
            return self.relation_tags
        raise KeyError(name)
