# Issues found: reasoning-collapse-puzzles (pilot and complete run)

| # | run | Issue | Severity | Status |
|---|---|---|---|---|
| 01 | pilot | [RSA private key in .local/ of the source snapshot](01-private-key-in-local.md) | Security | Fixed for GitHub (never committed). Rotate if it was ever authorized |
| 02 | complete | [Verdict locked by censoring gate](02-verdict-locked-by-censoring-gate.md) | High (design) | Documented. GPU completion (~24 CU) not recommended, because it cannot change H2/H3 |
| 03 | complete | [Stale writeup/blog; missing screenshot](03-stale-writeup-and-missing-screenshot.md) | Medium | The newsletter post uses the final 417 records |
| 04 | complete | [Program arm not like-for-like](04-program-arm-not-like-for-like.md) | Medium | Disclosed |

The [pilot-run](../pilot-run/) folder also notes that it is superseded by the [complete run](../complete-run/) (465/750 responses missing there).
