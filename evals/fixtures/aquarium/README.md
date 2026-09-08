# Eval fixtures

A frozen copy of the aquarium data, used by `./shrimpy eval`. Each case gets its
own temp copy, so cases run in parallel without seeing each other's writes.

**This is a third, separate thing.** Not the live data (that is on the volume,
`$HERMES_HOME/workspace/aquarium/`), and not the skill's bundled migration payload
(`skills/aquarium/aquarium-supervisor/assets/initial/`). It is fixed test data, so
a case's assertions do not move the day someone logs a real reading.

It starts as a copy of the migration payload and is expected to diverge. When it
changes, `harness/snapshot.py::definition_sha` invalidates every eval snapshot —
fixtures change the answer, so they must.
