# Phase III Implementation Plan: Decision Layer & Calibration

## Context

The Hotix engine has successfully completed **Phase I** (core market structure engine) and **Phase II** (market context layer). The system now:

- Analyzes 8 indices with 17 computed features
- Classifies 5 state dimensions per index
- Detects 6 pattern types and 4 transition types
- Computes 7 pair relationships with relative strength analysis
- Determines 4 market regimes and 4 trading contexts
- Outputs full JSON + Markdown with complete traceability
- Has **51 passing tests** with TDD discipline

**Current Output** (`market_context`):
```json
{
  "label": "Cash",
  "score": 5.0,
  "confidence": 0.71,
  "allowed_styles": ["观察", "复盘", "等待"],
  "disallowed_styles": ["主动进攻", "高频试错", "重仓出击"],
  "risk_budget": {"total_exposure": 0.10, "max_positions": 1, "max_single_name_weight": 0.05}
}
```

**The Gap**: Context is still **style-level descriptive** ("观察/复盘/等待"), not **setup-level executable** ("突破追涨：禁止", "低位修复：仅限小仓"). The system infers market structure but doesn't yet translate it into actionable trading permissions with explicit conflict resolution.

---

## Problem Statement

The existing DSL pipeline stops at `contexts`:

```
features → states → patterns → transitions → pair_features → pair_states → 
relation_tags → regimes → contexts ✅ (implemented)
```

Missing layers to bridge from inference to execution:

1. **Policy DSL** — Translate context/regime/salience into concrete setup permissions
2. **Conflict DSL** — Explicit conflict resolution with overrides and vetoes
3. **Context State Machine** — Track prev→current context transitions at market level
4. **Validation & Calibration Engine** — Historical statistics, rule hit analysis, distribution monitoring

These layers are documented in `docs/SRS/Phase III/PhaseIII-Planning.md` but **not yet implemented**.

---

## What Phase III Documents Propose

Three new DSL files per the detailed design documents:

### 1. `policies.yaml` (Policy DSL v1)
Maps context labels + market conditions → setup_permissions + execution_constraints + vetoes

- 7 setup types: `breakout`, `continuation_pullback`, `low_level_repair`, `defensive_core_rotation`, `high_beta_chase`, `reversal_catch`, `trend_follow`
- Status hierarchy: `forbidden > restricted > probe_only > allowed`
- Size hierarchy: `none < tiny < small < normal < large`
- Execution constraints: `max_new_positions`, `intraday_addons`, `require_confirmation`, `allow_gap_chase`, `allow_average_up`
- Priority-based override (higher priority wins, same priority = last-write)

### 2. `conflicts.yaml` (Conflict DSL v1)
Explicit conflict detection and resolution

Effects:
- `force_context` / `cap_context_to` — override context selection
- `block_context_upgrade` — prevent upgrading to more aggressive context
- `force_policy` — directly set policy fields
- `confidence_delta` — adjust final confidence
- `add_veto` — add veto reasons

### 3. `context_transitions.yaml` (State Machine DSL v1)
Market-level context transition tags (distinct from asset-level `transitions.yaml`)

Detects:
- `Cash → Caution`: 现金期尝试修复
- `Caution → Offense`: 进攻环境确认
- `Offense → Caution`: 进攻降速
- `Caution → Cash`: 结构丢失退回现金
- Persistence tags: 现金期延续 / 进攻环境延续 / 防守环境延续

### 4. `validation_engine.py` (Calibration Engine v1)
Historical replay and rule effectiveness analysis:
- Distribution statistics (regime/context/tag frequencies)
- Transition matrices
- Rule hit rate analysis (never-hit / always-hit detection)
- Misjudgment case tracking
- Calibration comparison workflow

---

## Implementation Roadmap (3 Phases)

### Phase III-A: Policy Engine (Week 1-2)
**Goal**: Context → executable permissions

**New Files**:
- `market_system/dsl/policies.yaml` — policy DSL (8-12 rules)
- `market_system/engine/policy_engine.py` — policy evaluator
- `tests/unit/test_policy_engine.py` — unit tests
- `tests/integration/test_policy_integration.py` — pipeline integration

**Schema**:
```python
@dataclass
class PolicyOutput:
    setup_permissions: dict[str, SetupPermission]
    execution_constraints: ExecutionConstraints
    vetoes: list[str]
    trace: dict
```

**Update**:
- `pipeline.py` — add `score_policy()` after `score_market_context()`
- `output_writer.py` — render policy in markdown
- `debug_report.py` — add policy extraction
- `validator.py` — validate `policies.yaml` schema

**Tests**:
- Policy selection matches expected permissions for each context
- Priority-based override works correctly
- Veto accumulation works
- Integration test verifies policy in full pipeline output

---

### Phase III-B: Conflict & State Machine (Week 3)
**Goal**: Explicit conflict resolution + context transition tracking

**New Files**:
- `market_system/dsl/conflicts.yaml` — conflict rules (6-8 rules)
- `market_system/dsl/context_transitions.yaml` — transition rules (6-8 rules)
- `market_system/engine/conflict_engine.py` — conflict evaluator
- `market_system/engine/context_transition_engine.py` — transition detector
- `tests/unit/test_conflict_engine.py`
- `tests/unit/test_context_transition_engine.py`

**Update**:
- `models.py` — add `ConflictOutput`, `ContextTransitionOutput` dataclasses
- `pipeline.py` — add `detect_conflicts()` and `detect_context_transition(prev_market, curr_market)`
- Need `prev_market` state — requires storing previous day's `market_context`
- `output_writer.py` — render conflicts + transition
- `validator.py` — validate conflicts/transitions schemas

**Tests**:
- Conflict detection identifies correct active conflicts
- Confidence delta accumulation correct
- Context transition detection uses `prev.market_context.label`
- Integration test with 2-day range verifies transition tags

---

### Phase III-C: Validation & Calibration (Week 4-5)
**Goal**: Historical statistics and rule effectiveness analysis

**New Files**:
- `market_system/engine/validation_engine.py` — batch replay and statistics
- `scripts/run_validation.py` — CLI for validation runs
- `scripts/compare_calibration.py` — before/after comparison
- `tests/unit/test_validation_engine.py`

**Features**:
```python
class ValidationEngine:
    def replay_range(start, end) -> list[dict]  # Full pipeline replay
    def compute_regime_distribution() -> pd.DataFrame
    def compute_context_distribution() -> pd.DataFrame
    def compute_tag_frequency() -> pd.DataFrame
    def compute_transition_matrices() -> dict[str, pd.DataFrame]
    def analyze_rule_hits() -> pd.DataFrame  # hit_rate per rule
    def find_never_hit_rules() -> list[str]
    def find_always_hit_rules() -> list[str]
```

**Outputs** (`market_system/outputs/stats/`):
- `regime_distribution.csv`
- `context_distribution.csv`
- `tag_frequency.csv`
- `regime_transition_matrix.csv`
- `context_transition_matrix.csv`
- `rule_hit_stats.csv`

**Outputs** (`market_system/outputs/calibration_runs/`):
- Timestamped run directories with before/after JSON + diff report

**Tests**:
- Statistics match manual calculations on fixture data
- Transition matrix diagonal dominance reasonable
- Never-hit rules correctly identified

---

## Critical Design Decisions

### Decision 1: Policy Merge Semantics
**Rule**: Higher `priority` wins. Same priority → last-write-wins (file order).

**Rationale**: Matches existing `contexts.yaml` behavior (priority 100 for base, 90 for bonus). Simple to reason about.

**Conservative override mode** (future): When two rules with same priority conflict on `status`, take more conservative value (`forbidden > restricted > probe_only > allowed`).

### Decision 2: Context Transition Prev State
**Requirement**: `context_transitions` needs `prev.market_context.label`.

**Implementation**: Store `prev_market_context` in `pipeline.py` as we iterate dates. For first date, `prev_context = None` → transitions don't fire (or use special "initial" state).

**API change**: `run_date_range()` will accumulate `prev_market` and attach `context_transition` to each payload's `market` section.

### Decision 3: Policy Trace Structure
Add to `market.trace`:
```python
market.trace["policy"] = {
    "matched_rules": [...],  # all policy rules that fired
    "final_permissions": {...},  # resolved permissions
    "vetoes": [...]
}
```

### Decision 4: Decision Output Schema v1
Final `market` payload structure:
```json
{
  "date": "...",
  "relation_tags": [...],
  "top_positive": [...],
  "top_negative": [...],
  "top_warning": [...],
  "top_transition": [...],
  "market_regime": {label, score, confidence, evidence},
  "market_context": {label, score, confidence, allowed_styles, disallowed_styles, risk_budget, runner_up, runner_up_score},
  "policy": {setup_permissions, execution_constraints, vetoes, trace},
  "conflicts": {active, confidence_delta_sum, block_context_upgrade},
  "context_transition": {prev_label, current_label, tags},
  "trace": {regimes, contexts, policy, conflicts, transitions}
}
```

### Decision 5: DSL File Registration
Add new DSL files to `loader.py`:
```python
DSL_FILES = [
    # ... existing
    "policies.yaml",
    "conflicts.yaml",
    "context_transitions.yaml",
]
```

And `validator.py` schema checks for each.

---

## Dependencies

| Module | Depends On |
|--------|-----------|
| `policy_engine.py` | `context_engine.py` (needs `market_context`), `resolver.py`, `expression.py` |
| `conflict_engine.py` | `policy_engine.py` output, `market_context`, `salience` |
| `context_transition_engine.py` | `prev.market_context` (stateful), `current.market_context` |
| `validation_engine.py` | Full pipeline, pandas for stats, needs multi-date replay |

**Order of Implementation**: Policy → Conflict → Transition → Validation

---

## Testing Strategy

### Unit Tests (per engine module)
- Mock resolver and runtime objects
- Test each DSL rule fires correctly
- Test priority override logic
- Test conflict effect application
- Test transition detection with prev/current

### Integration Tests
- Extend `tests/integration/test_pipeline.py` with:
  - `test_policy_included_in_output`
  - `test_conflicts_detected_correctly`
  - `test_context_transition_tags_attached`
  - `test_validation_engine_produces_stats`

### Golden Tests
- Update golden JSON to include `policy`, `conflicts`, `context_transition`
- Existing golden test will fail initially → update after implementation

### Validation Tests
- `test_validation_engine_statistics_are_deterministic`
- `test_rule_hit_stats_match_trace_data`

---

## Verification Steps

### 1. Unit Verification
```bash
pytest tests/unit/test_policy_engine.py -v
pytest tests/unit/test_conflict_engine.py -v
pytest tests/unit/test_context_transition_engine.py -v
pytest tests/unit/test_validation_engine.py -v
```

### 2. Integration Verification
```bash
pytest tests/integration/test_pipeline.py::test_policy_included_in_output -v
pytest tests/integration/test_pipeline.py::test_conflicts_detected_correctly -v
pytest tests/integration/test_pipeline.py::test_context_transition_tags_attached -v
```

### 3. Golden File Verification
```bash
pytest tests/golden/test_golden_daily.py -v
# Expected: FAIL initially (new fields), then PASS after golden update
```

### 4. CLI Verification
```bash
python -m market_system.run_daily --date 2026-04-05 --data-dir market_system/tests/fixtures --dump-json
# Verify policy, conflicts, context_transition in output

python -m market_system.run_daily --start 2026-04-03 --end 2026-04-05 --write-files
# Verify files written with new fields

# Validation CLI
python scripts/run_validation.py --start 2026-04-03 --end 2026-04-05
# Verify stats CSVs written to outputs/stats/
```

### 5. Regression Verification
```bash
pytest tests/ -q  # All 51 existing tests must still pass
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Policy rules conflict ambiguously | Medium | Define clear priority + conservative fallback; document merge semantics |
| Context transition prev-state not available for first date | Low | Special case: no transition for first date in range |
| Performance degradation from extra passes | Low | All new engines are O(rules) — negligible vs feature computation |
| DSL validation misses policy/conflict schemas | Medium | Extend `validator.py` before writing YAML files |
| Golden file churn from new fields | Low | Accept intentional churn — update golden once implementation stable |
| `eval()` security concerns in new rules | Already present | Reuse existing `expression.py` safe eval (same risk profile) |

---

## Files to Modify

### Create (8 new files)
1. `market_system/dsl/policies.yaml`
2. `market_system/dsl/conflicts.yaml`
3. `market_system/dsl/context_transitions.yaml`
4. `market_system/engine/policy_engine.py`
5. `market_system/engine/conflict_engine.py`
6. `market_system/engine/context_transition_engine.py`
7. `market_system/engine/validation_engine.py`
8. `scripts/run_validation.py`

### Modify (7 existing files)
9. `market_system/engine/models.py` — add `PolicyOutput`, `ConflictOutput`, `ContextTransitionOutput` dataclasses
10. `market_system/engine/pipeline.py` — add 4 new pipeline stages, track prev_market
11. `market_system/engine/output_writer.py` — render new sections in markdown
12. `market_system/engine/debug_report.py` — add policy/conflict/transition extraction
13. `market_system/engine/validator.py` — extend schema validation for 3 new DSL types
14. `market_system/engine/loader.py` — add 3 new DSL files to `DSL_FILES`
15. `tests/integration/test_pipeline.py` — add integration tests for new stages

### Tests (4 new test modules)
16. `tests/unit/test_policy_engine.py`
17. `tests/unit/test_conflict_engine.py`
18. `tests/unit/test_context_transition_engine.py`
19. `tests/unit/test_validation_engine.py`

---

## Acceptance Criteria

Phase III-A (Policy) complete when:
- [ ] `policies.yaml` has at least 8 rules covering all 4 contexts
- [ ] `policy_engine.py` produces deterministic permissions per context
- [ ] Policy appears in JSON output under `market.policy`
- [ ] Policy rendered in Markdown output
- [ ] Unit + integration tests pass
- [ ] Existing 51 tests still pass

Phase III-B (Conflict + Transition) complete when:
- [ ] `conflicts.yaml` has at least 6 rules covering major conflict patterns
- [ ] `context_transitions.yaml` has 6-8 rules for all transitions + persistence
- [ ] `conflicts` and `context_transition` appear in JSON output
- [ ] `prev.market_context` correctly supplied for 2+ day range
- [ ] Transition tags correctly attached to payload
- [ ] All tests pass

Phase III-C (Validation) complete when:
- [ ] `validation_engine.py` can replay any date range
- [ ] All 6 statistic types generate without error
- [ ] `scripts/run_validation.py` CLI works end-to-end
- [ ] Stats CSVs readable and reasonable (no empty distributions)
- [ ] Rule hit analysis correctly identifies rules from trace data

---

## Implementation Sequence (Day-by-Day)

### Day 1-2: Policy Engine
1. Add DSL files to `loader.py` + `validator.py`
2. Create `models.py` additions (`PolicyOutput`, `SetupPermission`, `ExecutionConstraints`)
3. Write `policy_engine.py` (evaluate all policy rules, merge by priority, apply conservative overrides)
4. Update `pipeline.py:run_single_date()` → call `score_policy()` after context
5. Update `output_writer.py` markdown template
6. Write unit tests for policy engine (mock contexts, verify permissions)
7. Write integration test (full pipeline check)
8. Run full test suite → fix breaks

### Day 3: Conflict Engine
1. Create `conflict_engine.py` (evaluate conflicts, apply effects, accumulate confidence_delta)
2. Add `ConflictOutput` to `models.py`
3. Extend `pipeline.py` → call `detect_conflicts()` after policy
4. Update output writer + debug report
5. Update validator for `conflicts.yaml` schema
6. Write `conflicts.yaml` with 6-7 rules
7. Unit + integration tests

### Day 4: Context Transition Engine
1. Create `context_transition_engine.py` (needs `prev_market_context`)
2. Add `ContextTransitionOutput` to `models.py`
3. Modify `pipeline.py:run_date_range()` to carry `prev_market` and call transition detector
4. For single-date runs: transition tags empty (no prev)
5. Write `context_transitions.yaml` (6-8 rules)
6. Update output + debug + validator
7. Tests: unit + integration with date range

### Day 5-6: Validation Engine
1. Design `ValidationEngine` class — batch replay over date range
2. Implement statistic collectors (use pandas groupby/crosstab)
3. Implement rule hit analyzer (iterate all trace data)
4. Implement transition matrix builder
5. Create `scripts/run_validation.py` CLI
6. Write unit tests with small fixture range
7. Test on full fixture set (16 dates)
8. Document output format

### Day 7: Polish & Documentation
1. Update `README.md` with Phase III features
2. Update golden JSON file
3. Full regression test run
4. Code review pass for style (black/ruff/mypy)
5. Add module docstrings
6. Write `docs/Phase III/Decision Layer Implementation.md`

---

## Success Metrics

Quantitative:
- [ ] All 51 existing tests pass
- [ ] 25+ new tests added (total ≥ 76)
- [ ] Policy/conflict/transition appear in JSON output
- [ ] Validation engine completes 16-date range in < 30 seconds
- [ ] Code coverage ≥ 90% on new modules

Qualitative:
- [ ] Policy permissions are contextually appropriate (review with domain expert)
- [ ] Conflict explanations are human-readable
- [ ] Transition tags reflect intuitive state changes
- [ ] Validation statistics are interpretable

---

## Next Immediate Step

**Start Phase III-A implementation**:

1. Create `market_system/dsl/policies.yaml` with base policies for Offense/Caution/Defense/Cash
2. Extend `loader.py` DSL_FILES list
3. Extend `validator.py` with policy schema validation
4. Create `models.py` additions
5. Implement `policy_engine.py:score_policy()`
6. Wire into `pipeline.py`
7. Write failing unit test for policy selection
8. Run → watch it fail → implement → pass
