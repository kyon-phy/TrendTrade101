# Observed network blocker

The saved cloud research environment's first representative Yahoo request was:

```text
https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=60d&interval=5m&events=div%2Csplits&includePrePost=false
```

Requested hostname: `query1.finance.yahoo.com`.

Observed error at 2026-10-03 13:47:06 UTC:

```text
<urlopen error Tunnel connection failed: 403 Forbidden>
```

Read-only inspection of `/etc/codex/network-policy.json` found a restricted HTTP egress policy and no allowlist entry for that hostname. Environment proxy configuration routes HTTPS through the managed proxy. This is consistent with the CONNECT tunnel being denied before a Yahoo application response.

No further affected price requests were made. No proxy, DNS, certificate, security setting or network policy was changed. No alternate hostname or other execution environment was used to obtain the denied prices.

Required setup: the environment owner must authorize access to `query1.finance.yahoo.com` through the normal cloud-environment internet settings. Repository access and the derived public input route do not grant Yahoo access. After setup, perform one ordinary preflight against the same approved endpoint before resuming capture. This document does not authorize making that settings change automatically.

Library transfers previously failed with a generic download error. The supported materialization workflow was stopped after bounded retries. The separately authorized Git input route now supplies explicitly derived public configuration files; it does not claim that original Library bytes were downloaded.
