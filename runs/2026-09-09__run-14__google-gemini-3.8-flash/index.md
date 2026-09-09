# Eval run — 14

| | |
|---|---|
| Result | **15/16 passed** |
| Model | `google/gemini-3.8-flash` |
| Spent | $0.4350 |
| Tokens | 801,928 |
| Started | 20260909T034411_681887Z |
| Commit | `067fdb6` |

## Cases

| Case | Result | Skills | CLI calls | Tokens | Cost | Transcript |
|---|---|---|---|--:|--:|---|
| casual-trigger | PASS | aquarium-supervisor | 1 | 57,502 | $0.0261 | [read](cases/casual-trigger.md) |
| bare-sensor-paste | PASS | aquarium-supervisor | 9 | 122,510 | $0.0537 | [read](cases/bare-sensor-paste.md) |
| which-tank | PASS | aquarium-supervisor | 3 | 57,925 | $0.0294 | [read](cases/which-tank.md) |
| dose-display | PASS | aquarium-supervisor | 2 | 45,421 | $0.0308 | [read](cases/dose-display.md) |
| dose-staging | PASS | aquarium-supervisor | 2 | 45,049 | $0.0243 | [read](cases/dose-staging.md) |
| orp-not-ammonia | PASS | aquarium-supervisor | 1 | 34,851 | $0.0272 | [read](cases/orp-not-ammonia.md) |
| no-invented-numbers | PASS | aquarium-supervisor | 1 | 32,507 | $0.0202 | [read](cases/no-invented-numbers.md) |
| coral-scope | PASS | aquarium-supervisor | 3 | 76,110 | $0.0326 | [read](cases/coral-scope.md) |
| salt-never | PASS | aquarium-supervisor | 1 | 63,750 | $0.0284 | [read](cases/salt-never.md) |
| cannot-check-sensor | PASS | aquarium-supervisor | 1 | 32,460 | $0.0251 | [read](cases/cannot-check-sensor.md) |
| does-not-run-aquadirector | PASS | aquarium-supervisor | 1 | 32,718 | $0.0209 | [read](cases/does-not-run-aquadirector.md) |
| status-first | PASS | aquarium-supervisor | 1 | 32,647 | $0.0207 | [read](cases/status-first.md) |
| log-a-reading | PASS | aquarium-supervisor | 3 | 58,169 | $0.0299 | [read](cases/log-a-reading.md) |
| no-recall-of-stale-numbers | PASS | aquarium-supervisor | 1 | 32,439 | $0.0199 | [read](cases/no-recall-of-stale-numbers.md) |
| report-on-request | PASS | aquarium-supervisor | 2 | 45,526 | $0.0261 | [read](cases/report-on-request.md) |
| brevity | **FAIL** | aquarium-supervisor | 1 | 32,344 | $0.0196 | [read](cases/brevity.md) |

Raw messages for each case sit beside the rendered file as `cases/<case>.json`, so a renderer fix can re-render an archived run.

## What failed

### brevity

- none of ['THIS_WILL_NEVER_MATCH_deliberate_ci_probe'] matched
