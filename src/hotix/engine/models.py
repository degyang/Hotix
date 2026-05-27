from dataclasses import asdict, dataclass, field


@dataclass
class SalienceItem:
    id: str
    rule_id: str | None
    date: str
    scope: str
    asset_id: str | None
    dimension: str
    category: str
    polarity: str
    score: float
    severity: str
    confidence: float
    freshness: str
    reason: str
    evidence: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    universe_id: str | None = None
    rank: int | None = None
    metric: str | None = None
    direction: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


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


@dataclass
class MarketRuntime:
    date: str
    relation_tags: list[str] = field(default_factory=list)
    top_positive: list[dict] = field(default_factory=list)
    top_negative: list[dict] = field(default_factory=list)
    top_warning: list[dict] = field(default_factory=list)
    top_transition: list[dict] = field(default_factory=list)
    market_regime: dict = field(default_factory=dict)
    market_context: dict = field(default_factory=dict)
    policy: dict = field(default_factory=dict)
    trace: dict = field(default_factory=dict)


@dataclass
class SetupPermission:
    status: str = "restricted"
    size: str = "small"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionConstraints:
    max_new_positions: int = 1
    intraday_addons: bool = False
    require_confirmation: bool = True
    allow_gap_chase: bool = False
    allow_average_up: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PolicyOutput:
    setup_permissions: dict = field(default_factory=dict)
    execution_constraints: dict = field(default_factory=dict)
    vetoes: list[str] = field(default_factory=list)
    trace: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
