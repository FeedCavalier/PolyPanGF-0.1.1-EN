# Validation

Version 0.1.1 was checked in an independent Python 3.14 environment on Ubuntu.

- All 17 regression tests passed, including portable exports, checksum verification, HTML links, biological identifiers, transactional updates, input validation and species-level occupancy.
- Ruff formatting and undefined-name checks passed.
- The synthetic example completed preparation, identification, orthology, pan-family classification, protein properties, expression, enrichment, TE profiles, plotting and reporting.
- The release wheel was built independently from the source distribution.
- Release text, filenames and nested wheel contents were scanned for machine-specific paths, network addresses and non-English text.

The native external-tool benchmarks documented for version 0.1.0 were not repeated in this packaging update. The bundled example uses imported family assignments and simulated expression and TE data.

Example locations in this distribution are virtual. Runtime checks should be repeated for the external tools selected by each user.
