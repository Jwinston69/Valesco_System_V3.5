\# Valesco v2.0 — CE Bundle Generator Specification

Version: 1.0

Status: Planning / Architectural

Scope: Defines the behaviour, phases, and CLI for the CE Bundle Generator tool.



-------------------------------------------------------------------------------

1\. PURPOSE

-------------------------------------------------------------------------------

The CE Bundle Generator is a single tool that produces the v2.0 Context Engineering

Bundle as specified in `VALESCO\_CE\_EXPORT\_SPEC\_v2.0.md`.



It:



\- Validates all core YAML and governance inputs

\- Ensures chunk datasets are present and in sync

\- Computes integrity hashes

\- Assembles a deterministic ZIP bundle for agent consumption

\- Enforces the Air Gap (read-only access to authoritative files)



The Generator is a local, trusted process. Agents may REQUEST a bundle but never

execute the generator themselves.



-------------------------------------------------------------------------------

2\. ENTRYPOINT \& CLI

-------------------------------------------------------------------------------



The generator will be implemented as a Python script:



&nbsp; engine/scripts/context\_engineering/bundle\_generator.py



CLI (initial v2.0):



&nbsp; engine\\python\_runtime\\python.exe engine\\scripts\\context\_engineering\\bundle\_generator.py ^

&nbsp;     --output "workspace/outputs/VALESCO\_CE\_BUNDLE.zip" ^

&nbsp;     \[--snapshot-id SNAP\_YYYY-MM-DD\_LABEL] ^

&nbsp;     \[--regenerate-chunks] ^

&nbsp;     \[--dry-run]



2.1 Required Arguments



\- --output <path>

&nbsp; Absolute or relative path to the output ZIP file.

&nbsp; Parent folder must exist or be creatable.



2.2 Optional Arguments



\- --snapshot-id <id>

&nbsp; If provided, the tool may load additional snapshot metadata (future feature).

&nbsp; For v2.0 MVP, this is accepted but not mandatory to implement.



\- --regenerate-chunks

&nbsp; If present, the generator will:

&nbsp;   - Re-run material\_chunker.py

&nbsp;   - Re-run task\_chunker.py

&nbsp;   - Re-run pack\_chunker.py

&nbsp;   - Re-run subcontractor\_chunker.py

&nbsp; into workspace/vector\_input/\* before bundling.



\- --dry-run

&nbsp; Perform all validation and hashing steps but do not write the ZIP file.

&nbsp; Useful for CI checks.



-------------------------------------------------------------------------------

3\. INPUTS

-------------------------------------------------------------------------------



3.1 Governance Files

\- docs/valesco\_instructions.txt

\- docs/governance/VALESCO\_TRUTH\_HIERARCHY.md

\- docs/governance/VALESCO\_DEVELOPER\_CHECKLIST.md

\- docs/VALESCO\_SYSTEM\_MANIFEST\_v1.9.1.md (or later)



3.2 Configuration

\- engine/config/materials\_allocator.yaml



3.3 Core Library

\- library/core/valesco\_materials.yaml

\- library/core/valesco\_tasks.yaml

\- library/core/valesco\_subcontractors.yaml



3.4 Pack

\- library/packs/valesco\_pack.yaml



3.5 Chunk Datasets

\- workspace/vector\_input/materials.jsonl

\- workspace/vector\_input/tasks.jsonl

\- workspace/vector\_input/pack.jsonl

\- workspace/vector\_input/subs.jsonl



3.6 Optional Snapshot Meta (v2.0+)

\- workspace/snapshots/<SNAP\_...>.json or .txt (future integration)



-------------------------------------------------------------------------------

4\. OUTPUTS

-------------------------------------------------------------------------------



4.1 ZIP Bundle

\- A single ZIP archive at the path specified by --output.



ZIP internal structure (must match CE Export Spec):



&nbsp; governance/

&nbsp;   valesco\_instructions.txt

&nbsp;   VALESCO\_TRUTH\_HIERARCHY.md

&nbsp;   VALESCO\_DEVELOPER\_CHECKLIST.md

&nbsp;   manifest.md



&nbsp; allocator/

&nbsp;   materials\_allocator.yaml



&nbsp; library/

&nbsp;   valesco\_materials.yaml

&nbsp;   valesco\_tasks.yaml

&nbsp;   valesco\_subcontractors.yaml



&nbsp; pack/

&nbsp;   valesco\_pack.yaml



&nbsp; chunks/

&nbsp;   materials.jsonl

&nbsp;   tasks.jsonl

&nbsp;   pack.jsonl

&nbsp;   subs.jsonl



&nbsp; meta/

&nbsp;   version\_info.json

&nbsp;   sha256\_all.txt

&nbsp;   snapshot\_meta.json (optional)



-------------------------------------------------------------------------------

5\. PROCESS PHASES

-------------------------------------------------------------------------------



The generator runs in clearly defined phases:



PHASE 1: DISCOVERY \& EXISTENCE CHECK

\- Confirm all required files exist.

\- If any required file is missing → FAIL with clear error code.



PHASE 2: VALIDATION GATE (HARD BLOCK)

\- Call existing validation routines (either via:

&nbsp;   - direct Python import of validate functions, or

&nbsp;   - invoking validate.bat / validate.py)

\- Enforce:

&nbsp; - YAML parse OK

&nbsp; - Schema conformity

&nbsp; - Cross-file integrity:

&nbsp;   - material codes referenced in tasks exist

&nbsp;   - unit whitelist respected

&nbsp;   - rates non-negative

&nbsp;   - zero-productivity not present

\- If any ERROR is found (per valesco\_instructions.txt) → abort.



PHASE 3: CHUNK CONSISTENCY (HARD BLOCK)

\- Load:

&nbsp;   workspace/vector\_input/materials.jsonl

&nbsp;   workspace/vector\_input/tasks.jsonl

&nbsp;   workspace/vector\_input/pack.jsonl

&nbsp;   workspace/vector\_input/subs.jsonl

\- Run the chunk\_audit logic:

&nbsp;   - counts for each domain match YAML

\- If --regenerate-chunks is passed:

&nbsp;   - re-run all chunkers before audit.

\- If any mismatch is detected → abort.



PHASE 4: HASHING \& VERSION METADATA

\- Compute SHA256 for each file included in the bundle.

\- Read version metadata from:

&nbsp;   - meta sections of YAML files

&nbsp;   - manifest version

\- Construct meta/version\_info.json with:

&nbsp;   - bundle\_version

&nbsp;   - created\_utc

&nbsp;   - pack/tasks/materials/subcontractors/allocator versions

&nbsp;   - SHA256 hashes.



\- Compute an overall hash summary (sha256\_all.txt):

&nbsp;   - one line per file: "<hash>  <relative\_path>"



PHASE 5: PACKAGING

\- Create an in-memory or on-disk ZIP file.

\- Add each file at its correct internal path.

\- Ensure binary/text modes are correct.

\- Ensure no temp files are left behind on failure.



PHASE 6: FINAL REPORT

\- Print:

&nbsp;   - bundle path

&nbsp;   - number of files added

&nbsp;   - hash of the bundle

\- Exit code:

&nbsp;   - 0 on success

&nbsp;   - non-zero on failure.



-------------------------------------------------------------------------------

6\. ERROR HANDLING \& CODES

-------------------------------------------------------------------------------



The generator must fail fast and clearly.



Typical error scenarios:



\- CONFIG-MISSING-FILE

\- CONFIG-YAML-PARSE-FAIL

\- VALIDATION-FAILED

\- CHUNK-AUDIT-FAILED

\- OUTPUT-PATH-INVALID

\- ZIP-WRITE-FAILED



Output format (stderr or stdout):



&nbsp; \[timestamp] | ERROR | CE-BUNDLE | code=VALIDATION-FAILED | message="Cross-file validation failed. See validator log."



Exit codes are aligned with CI use:

\- 0 = success

\- 1 = generic failure

\- 2 = validation failure

\- 3 = config/path failure

\- 4 = chunk mismatch



-------------------------------------------------------------------------------

7\. SECURITY \& AIR GAP

-------------------------------------------------------------------------------



7.1 Read-only Access

The generator must treat all library, pack, and governance files as read-only.



7.2 No Agent-originated Paths

\- Paths are static and defined by the system layout.

\- Agent requests may not inject arbitrary filesystem locations.



7.3 Deterministic Rebuild

\- Re-running the generator with identical inputs produces an identical bundle (same internal file contents and hash).

\- Timestamps are allowed to differ at filename/metadata level only.



-------------------------------------------------------------------------------

8\. EXTENSIBILITY (v2.1+)

-------------------------------------------------------------------------------



Future extensions may include:

\- Additional chunk domains (e.g. extensions, proposals)

\- Incremental bundles per project

\- Project-specific doc sets

\- Snapshot-replay bundles



These additions must not break the v2.0 bundle contract for agents.



-------------------------------------------------------------------------------

END OF DOCUMENT



