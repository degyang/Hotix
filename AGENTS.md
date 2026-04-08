# Execution Rules

- Default behavior: continue working until the user's requested result is fully delivered.
- Do not stop after intermediate milestones, partial implementations, or "good enough" states.
- Do not ask for confirmation between implementation stages unless:
  - a decision has non-obvious product tradeoffs, or
  - a destructive or risky action needs approval, or
  - required information is genuinely missing.
- Progress updates should be brief and should not be phrased like completion messages.
- If the requested result is not yet fully aligned with the spec, continue recursively until the remaining gaps are implemented.
- Before claiming completion, run the relevant tests and verify outputs.
