# Distribution privacy

Documentation paths such as `/path/to/project` and `/path/to/software/pSONIC.py` are virtual examples. Runnable synthetic examples use package-relative paths.

The public release is assembled from an explicit file allowlist. It includes source, documentation, synthetic example inputs, an installable wheel and aggregate validation results. Local caches, raw runtime logs, editable-install metadata, private connection files and machine-specific status snapshots are excluded.

Text and filenames are scanned for machine-specific identifiers and installation prefixes before release. Nested wheel contents are scanned as well. PDF, SVG and PNG workflow assets are included only after metadata review.

Local execution creates detailed provenance for reproducibility. Portable result exports replace recorded filesystem locations and host identifiers with virtual example values. The private-to-virtual lookup table is retained in memory during export. Biological tables retain their identifiers, with known machine-location prefixes sanitized where present.

`PORTABLE_EXPORT.json` describes export semantics. Stage manifests refer to execution-time hashes, and `EXPORT_SHA256SUMS.txt` validates the redistributed files. The local project remains the source for resumed analysis.
