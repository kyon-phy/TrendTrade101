# Public project inputs

These are sanitized public projections of TrendTrade101 configuration v0.15 and its frozen universe files. Original source identities remain unchanged; all source and public SHA256 checksums are recorded in [public_input_provenance.json](public_input_provenance.json).

- [TrendTrade101_Backtest_Configuration.md](TrendTrade101_Backtest_Configuration.md): complete v0.15 strategy specification, preserving all parameter tables and membership definitions
- [frozen_universe_members.csv](frozen_universe_members.csv): 201 ordered membership records and 127 unique market/ticker pairs
- [frozen_universe_manifest.json](frozen_universe_manifest.json): the eight exact ordered groups, provenance and limitations
- [frozen_universe_manifest.md](frozen_universe_manifest.md): readable membership interpretation

Sanitization removes one nonessential tracking query parameter from a WMT source URL and two unrelated archival/conversation references from the configuration. Manifest checksums are updated truthfully. No member, order, rule, model budget, source estimate or caveat has been changed. The only membership exception already present in the source is the approved US daily NKE-to-PYPL replacement.

The original pre-exception review snapshot is referenced by hash but is not bundled. Input validation must use the public hashes for these public files; an original-source hash is not a checksum of a derived file. The CSV retains its source UTF-8 BOM and line endings.

These files are configuration inputs and public-source metadata. They contain no raw vendor price cache or strategy return results. Their publication does not resolve price coverage, corporate actions, calendars, final-holdout boundaries, or other outstanding implementation audits.
