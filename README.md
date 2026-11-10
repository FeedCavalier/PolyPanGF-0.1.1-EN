# PolyPanGF

PolyPanGF 0.1.1 is an English-language toolkit for pan-gene-family analysis across mixed-ploidy genome assemblies. It combines family identification, orthogroup integration, occupancy and copy-number summaries, optional downstream analyses, figures and reports.

The toolkit records species occupancy, dataset copy number, biological ploidy and assembly representation as separate quantities. All paths shown in this documentation are relative examples or virtual placeholders.
![Uploading image.png…]()

## Installation

PolyPanGF supports Linux and Python 3.9 or later. Install the Python package from the source directory or the supplied wheel.

```bash
python -m pip install .
# Alternatively, install the wheel supplied in dist/
python -m pip install dist/polypangf-0.1.1-py3-none-any.whl
polypangf --version
```

An optional Conda environment specification includes the Python dependencies and external analysis programs.

```bash
conda env create -f environment.yml
conda activate polypangf-en
python -m pip install .
```

The pSONIC Python script is installed separately from its official repository. Its Python interpreter must provide igraph. Third-party programs retain their original licenses.

## Quick start

```bash
polypangf init demo
polypangf validate -c demo/config.json
polypangf doctor -c demo/config.json
polypangf run -c demo/config.json
polypangf run -c demo/config.json --resume
polypangf status -c demo/config.json --verify
polypangf export -c demo/config.json -o demo_results.zip
```

The generated example uses explicitly synthetic data. It exercises the Python workflow without requiring HMMER or orthology programs. Real biological analyses use user-supplied proteomes, annotations and analysis inputs.

## Commands

| Command | Function |
|---|---|
| `init` | Generate a runnable synthetic project |
| `validate` | Check configuration, manifest, FASTA and GFF3 inputs |
| `doctor` | Inspect dependencies required by the selected modules |
| `prepare` | Standardize IDs, map protein models and validate CDS translations |
| `identify` | Search HMM profiles or import candidates and select supported isoforms |
| `synteny` | Prepare whole-proteome OrthoFinder and MCScanX inputs for pSONIC |
| `orthology` | Import groups, run family OrthoFinder or invoke official pSONIC |
| `pan` | Calculate occupancy classes, presence matrices, copy counts and accumulation |
| `properties` | Calculate protein length, molecular weight, theoretical pI and GRAVY |
| `tree` | Run MAFFT and FastTree |
| `motifs` | Discover MEME motifs and scan all candidates with FIMO |
| `expression` | Summarize stage expression, Tau and within-group correlations |
| `enrichment` | Test GO, KEGG or custom annotation enrichment |
| `te` | Calculate oriented TE coverage and length-matched background profiles |
| `kaks` | Run MAFFT, PAL2NAL and PAML YN00 on eligible pairs |
| `duplication` | Import standardized duplication-type assignments |
| `markers` | Match processed single-nucleus or spatial marker records |
| `plot` | Export PDF, SVG and 300 dpi PNG figures |
| `report` | Generate an HTML report and Markdown summary |
| `run` | Execute the configured workflow |
| `status` | Inspect completed stages and failed work directories |
| `export` | Create a path-sanitized result ZIP with checksums |

Use `polypangf COMMAND --help` for command-specific options. Analysis commands accept the following common arguments.

| Option | Meaning |
|---|---|
| `-c`, `--config` | JSON or YAML configuration |
| `-o`, `--output` | Override the result directory |
| `-t`, `--threads` | External-program thread allocation |
| `--seed` | Random seed |
| `--resume` | Reuse outputs after input, code and output hash verification |
| `--force` | Recompute target stages and prerequisites |
| `--dry-run` | Print the execution plan without creating analysis output |
| `-v`, `--verbose` | Enable debug logging |
| `-q`, `--quiet` | Show errors and the final JSON result |

`run --stages identify,pan` selects target stages and resolves their prerequisites. `validate --quick` skips complete sequence parsing. `status --verify` checks output hashes. A single dataset supports independent identification and protein-property analyses. Pan-family comparisons require at least two independent occupancy units.

## Dataset manifest

The manifest is a tab-separated table. File paths are interpreted relative to the manifest. Required columns follow.

| Column | Meaning |
|---|---|
| `dataset` | Unique assembly or material code, starting with a letter |
| `species` | Species identifier shared by assemblies of the same species |
| `ploidy` | Biological ploidy, such as 2, 4 or 8 |
| `represented_sets` | Basic chromosome sets or phased complements represented by the input |
| `proteins` | Protein FASTA, optionally gzip-compressed |

Optional columns are `gff`, `cds`, `model_map`, `role` and `relative_ploidy`. Dataset names support letters, digits, underscores and hyphens. `role` accepts `analysis` or `outgroup`. Outgroups contribute to orthology inference. Occupancy summaries use analysis datasets.

Automatic pSONIC preparation requires an explicit positive `relative_ploidy` for every dataset. These values describe relative copy expectations for the compared lineages.

`model_map` requires `protein_id` and `gene_id`. Optional columns are `transcript_id`, `cds_id` and `unit_type`. Use a unique protein identifier with `unit_type=protein` for an unmapped model. The toolkit flags protein-based units as `protein_id_assumption`. Namespaces separate identical original IDs from different datasets.

GFF3 coordinates are 1-based and closed. TE coordinates are 0-based and half-open. CDS sequences enter Ka/Ks analysis after successful frame and translation checks. Conflicting coordinates, duplicate FASTA IDs and shared placeholder locus IDs produce explicit errors.

The default invalid-protein policy is `error`. Set `preparation.invalid_protein` to `mask` to replace invalid residues with X, or to `skip` to exclude affected models. Actions are recorded in `prepare/sequence_audit.tsv`.

## Family configuration

```yaml
schema_version: 1
family: ExampleFamily
manifest: datasets.tsv
output: results
threads: 8
seed: 42
identification:
  profiles:
    - label: family_domain
      path: profiles/family_domain.hmm
      primary: true
    - label: accessory_domain
      path: profiles/accessory_domain.hmm
      primary: false
  domain_evalue: 1.0e-5
  min_domain_coverage: 0.0
  architecture_rules:
    - label: combined_architecture
      requires: [family_domain, accessory_domain]
    - label: family_domain_only
      requires: [family_domain]
orthology:
  backend: orthofinder
pan:
  unit: species
  softcore_fraction: 0.9
```

Profile files are supplied by the user. Architecture rules are evaluated in order. Detailed subfamily assignments can use specialized classifiers or curated references. Existing candidates can be supplied through `identification.candidates`, using columns `dataset`, `protein_id` and optional `architecture`.

## Orthology backends

### Imported groups

```yaml
orthology:
  backend: import
  groups: groups.tsv
```

The input accepts a long table with `group,dataset,gene_id` or an OrthoFinder-style wide table. Unknown members produce errors by default. Set `allow_nonfamily: true` when extracting a target family from whole-genome groups. Dataset columns must match declared datasets. Repeated or multiply assigned candidates produce errors. Unassigned candidates are reported separately.

### Family OrthoFinder

```yaml
orthology:
  backend: orthofinder
  search: diamond
```

This backend runs OrthoFinder on the identified family candidates and records the family-level inference scope.

### Native pSONIC

```yaml
orthology:
  backend: psonic
  script: /path/to/software/pSONIC.py
  python: /path/to/environment/bin/python
```

Automatic preparation runs whole-proteome OrthoFinder and MCScanX. Every representative must have usable coordinates. Family-supported representatives are selected for target-family loci, and the longest proteins represent other declared loci.

Precomputed whole-genome inputs can be supplied explicitly.

```yaml
orthology:
  backend: psonic
  script: /path/to/software/pSONIC.py
  prefix: /path/to/genome_inputs/project
  groups: /path/to/genome_inputs/Orthogroups.tsv
  sequence_ids: /path/to/genome_inputs/SequenceIDs.txt
  species_ids: /path/to/genome_inputs/SpeciesIDs.txt
  ploidy: /path/to/genome_inputs/relative_ploidy.tsv
```

The prefix identifies `.gff`, `.tandem` and `.collinearity` files with OrthoFinder-compatible gene codes. The relative-ploidy file contains one tab-separated line in OrthoFinder species-column order. The adapter restores column names to the official headerless output before extracting family members.

For MCScanX distributions that omit tandem-edge output, the adapter derives edges between adjacent genes supported by BLAST E-values no greater than 1e-5. The source is recorded in `tandem_source`. Precomputed input mode accepts externally prepared tandem edges.

## Occupancy and copy-number interpretation

`pan.unit` accepts `species` or `dataset`. Multiple assemblies of one species contribute one species-presence vote. Dataset copy counts are retained separately.

- Core groups occur in every occupancy unit.
- Specific groups occur in one unit.
- Softcore groups meet the configured occupancy threshold among the remaining groups.
- Shell groups contain the remaining multi-unit groups.

Unassigned candidates form a separate category. `copies_per_represented_set` divides observed copies by declared represented sets. It is a descriptive quantity whose interpretation depends on assembly and annotation completeness. Accumulation curves use the exact expected richness over all equally sized subsets.

## Optional analyses

```yaml
tree: {}
motifs:
  number: 10
  min_width: 6
  max_width: 50
  pvalue: 0.0001
expression:
  dataset: OCT
  matrix: expression.tsv
  samples: samples.tsv
  permutations: 19999
  min_max_expression: 1
enrichment:
  dataset: DIP
  database: GO
  term2gene: genome_GO.tsv
  min_term_size: 2
  fdr: 0.05
te:
  intervals: TE_intervals.tsv
  chrom_sizes: chromosome_sizes.tsv
  flank: 2000
  bins_per_region: 30
kaks:
  anchor: DIP
  min_codons: 50
  min_coverage: 0.7
  min_ks: 0.01
  max_ks: 2
  max_omega: 99
  timeout: 300
duplication:
  table: duplication_types.tsv
  source_method: DupGen_finder
markers:
  table: marker_records.tsv
  fdr: 0.05
```

### Expression

The matrix contains `gene_id` and numeric sample columns. Sample metadata contains `sample,stage`. Stages follow their first appearance in metadata, and replicate values are averaged per stage. Missing genes are recorded explicitly. Values must be finite and nonnegative.

Tau describes stage specificity. Within-group correlations use log(1+value) trajectories and equal weighting across evaluable multicopy groups. The one-sided permutation test fixes group sizes and uses a plus-one correction. This version provides unstratified permutations.

### Enrichment

Annotations contain `gene_id,term` and optional `description`. Annotated genes define the default background. An optional `background` table can specify gene IDs, and `valid_terms` can restrict terms to a species-appropriate catalog.

Whole-family tests and pooled coverage-class tests are adjusted separately. Each scope includes tested terms with zero foreground hits. Categories require annotated members, and Unassigned is evaluated separately. GO and KEGG can be run with separate configurations and result directories.

### TE environment

TE intervals contain `dataset,chrom,start,end`. Supply intervals already classified as TEs. Intersecting intervals are merged before coverage calculation. Background genes are selected from the same chromosome by nearest length, with anchor relationships retained when a background gene is reused.

`chrom_sizes` contains `dataset,chrom,length` and supports chromosome-boundary clipping. Missing TE chromosome records produce unavailable profiles. Without chromosome lengths, negative upstream coordinates are clipped to zero and terminal regions follow supplied coordinates.

### Ka/Ks and duplication

Ka/Ks analysis uses dataset pairs with one member each in the current group. Optional `anchor` restricts comparisons. Pair estimates, excluded comparisons and group medians are exported separately.

Duplication tables contain `dataset,gene_id,duplication_class`. Supported types are `wgd_segmental,tandem,proximal,transposed,dispersed,unsupported`. Missing assignments are labeled `not_evaluated`. This module imports results produced by tools such as DupGen_finder.

### Marker tables

Marker tables contain `dataset,gene_id,assay,stage,cluster,padj`. Matched records, significant membership breadth and unmatched records are exported separately. Full cell or spatial count-matrix clustering is performed using the corresponding specialist workflows.

## English runtime and portable exports

The CLI and external-program wrapper use `LANG=C.UTF-8`, `LC_ALL=C.UTF-8` and `LANGUAGE=en`. Input identifiers support UTF-8. English documentation, examples and release metadata use portable names and virtual example paths.

Each local stage records execution-time configuration, file hashes, elapsed time and provenance. A project lock prevents concurrent writes. Transactional stage publication retains the previous complete result when recomputation fails.

`export` replaces recorded machine paths and host identifiers with virtual example values in shared text artifacts. Relative HTML links are retained. Stage manifests describe execution-time hashes, while `EXPORT_SHA256SUMS.txt` verifies redistributed bytes. Use the local project directory for resumed analysis and the exported archive for review or sharing.

## Validation and development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

See `VALIDATION.md` for the release validation scope and `PRIVACY.md` for distribution checks. Functional regression checks and method-performance benchmarks are recorded as separate activities. Project release licensing is pending, and third-party software and data retain their source licenses.

## Method references

- pSONIC, DOI 10.1093/g3journal/jkab170. https://github.com/conJUSTover/pSONIC
- OrthoFinder, DOI 10.1186/s13059-019-1832-y. https://github.com/OrthoFinder/OrthoFinder
- MCScanX, DOI 10.1093/nar/gkr1293.
- HMMER, DOI 10.1371/journal.pcbi.1002195.
- MAFFT, DOI 10.1093/molbev/mst010.
- FastTree, DOI 10.1371/journal.pone.0009490.
- PAL2NAL, DOI 10.1093/nar/gkl315.
- YN00, DOI 10.1093/oxfordjournals.molbev.a026236.
