# Golden-set labeling rubric

Two independent labelers should reach the same `act_now` and `severity` for each case.

## `act_now`

| Label | When |
| --- | --- |
| `true` | Active or imminent user impact, SLO breach risk, unknown blast radius with credible signal, security/data-loss indicators, or paging-severity infrastructure failure |
| `false` | Clear noise, synthetic/test alerts, already-mitigated informational notices, single-host flapping with no corroboration, or capacity warnings scheduled for business hours with no worsening trend |

**Tie-break:** if a reasonable on-call would page *or* open an incident channel, label `act_now=true`. Prefer missing a false alarm over missing a real incident when labeling ambiguous-but-credible cases (`act_now=true`).

## `severity` (1–4)

| Level | Meaning | Examples |
| --- | --- | --- |
| 1 | Informational / no user impact | Successful cron, routine cert renewal notice, debug spam |
| 2 | Degraded but contained | Single replica restart loop, elevated latency under SLO, flaky canary |
| 3 | Active user impact or SLO risk | Error-rate climb affecting requests, regional brownout, queue backlog growing |
| 4 | Outage / data-loss / security | Multi-AZ outage, primary DB unreachable, ransomware indicators, auth broken globally |

Off-by-one disagreements on severity are expected at boundaries (2↔3); `act_now` must still agree.

## `rationale`

One sentence naming the decisive signal (impact, corroboration, or why it is noise).

## `expect_tool_call`

Set `true` when the alert text alone is insufficient and metrics would change the decision (sparse signal, possible false page). Used by trajectory suite later.
